from flask import Blueprint, request, jsonify, current_app
import uuid

from app.tasks import validation_task 
from app.tasks import preprocessing_tasks
from app.tasks import dataset_fetch_tasks
from app.utils import dataframe_processing
from app.utils import file_handler
from app.utils import redis_store
from app.services import dadosgov_client
from app.validators.descriptions import RULE_DESCRIPTIONS
from app.models import PreprocessingReport, ValidationReport, TaskStatus, ValidationRuleset
from app import db
from app import celery

validation_bp = Blueprint("validation", __name__)

# ============================================================
# Endpoint for fetching available validation rules

@validation_bp.route("/available_rules", methods=["GET"])
def available_rules():
    return jsonify(RULE_DESCRIPTIONS), 200


# ============================================================
# Endpoints for ValidationRuleset CRUD operations

@validation_bp.route("/validation_rulesets", methods=["POST"])
def create_validation_ruleset():
    """
    Accepts a JSON body with:
      - dadosgov_user_id: the dados.gov user identifier to associate the ruleset with
      - title: the title of the ruleset
      - description: a description of the ruleset
      - resource_id_list: a list of resource IDs that this ruleset applies to
      - rules: an array of rule objects, e.g. [{"dataframe_ids": ["df1"], "type": "not_null", "column": "Age"}, ...]
    """
    body = request.get_json(silent=False)  # raises 400 with a real error if body is bad
    if not body:
        return jsonify({"error": "Request body must be JSON"}), 400

    dadosgov_user_id = body.get("dadosgov_user_id")
    title = body.get("title")
    description = body.get("description")
    resource_id_list = body.get("resource_id_list")
    rules = body.get("rules")

    if not dadosgov_user_id or not title or not resource_id_list or not rules:
        return jsonify({"error": "Missing required fields"}), 400

    new_ruleset = ValidationRuleset(
        dadosgov_user_id=dadosgov_user_id,
        title=title,
        description=description,
        resource_id_list=resource_id_list,
        rules=rules
    )
    db.session.add(new_ruleset)
    db.session.commit()

    return jsonify({"message": "Validation ruleset created", "ruleset_id": new_ruleset.id}), 201


@validation_bp.route("/validation_rulesets/<int:ruleset_id>", methods=["GET"])
def get_validation_ruleset(ruleset_id):
    ruleset = ValidationRuleset.query.get(ruleset_id)
    if not ruleset:
        return jsonify({"error": "Validation ruleset not found"}), 404

    return jsonify({
        "id": ruleset.id,
        "dadosgov_user_id": ruleset.dadosgov_user_id,
        "title": ruleset.title,
        "description": ruleset.description,
        "resource_id_list": ruleset.resource_id_list,
        "rules": ruleset.rules,
        "created_at": ruleset.created_at.isoformat(),
        "updated_at": ruleset.updated_at.isoformat()
    }), 200


@validation_bp.route("/validation_rulesets/<int:dadosgov_user_id>", methods=["GET"])
def get_validation_rulesets_by_user_id(dadosgov_user_id):
    rulesets = ValidationRuleset.query.filter_by(dadosgov_user_id=dadosgov_user_id).all()
    if not rulesets:
        return jsonify({"error": "No validation rulesets found for the specified user"}), 404

    return jsonify([{
        "id": ruleset.id,
        "dadosgov_user_id": ruleset.dadosgov_user_id,
        "title": ruleset.title,
        "description": ruleset.description,
        "resource_id_list": ruleset.resource_id_list,
        "rules": ruleset.rules,
        "created_at": ruleset.created_at.isoformat(),
        "updated_at": ruleset.updated_at.isoformat()
    } for ruleset in rulesets]), 200


@validation_bp.route("/validation_rulesets/<int:ruleset_id>", methods=["PUT"])
def update_validation_ruleset(ruleset_id):
    ruleset = ValidationRuleset.query.get(ruleset_id)
    if not ruleset:
        return jsonify({"error": "Validation ruleset not found"}), 404

    body = request.get_json(silent=False)  # raises 400 with a real error if body is bad
    if not body:
        return jsonify({"error": "Request body must be JSON"}), 400

    ruleset.title = body.get("title", ruleset.title)
    ruleset.description = body.get("description", ruleset.description)
    ruleset.resource_id_list = body.get("resource_id_list", ruleset.resource_id_list)
    ruleset.rules = body.get("rules", ruleset.rules)

    db.session.commit()

    return jsonify({"message": "Validation ruleset updated"}), 200


@validation_bp.route("/validation_rulesets/<int:ruleset_id>", methods=["DELETE"])
def delete_validation_ruleset(ruleset_id):
    ruleset = ValidationRuleset.query.get(ruleset_id)
    if not ruleset:
        return jsonify({"error": "Validation ruleset not found"}), 404

    db.session.delete(ruleset)
    db.session.commit()

    return jsonify({"message": "Validation ruleset deleted"}), 200


# ============================================================
# Endpoints for fetching datasets from dados.gov

@validation_bp.route("/fetch_user_datasets_info", methods=["POST"])
def fetch_user_datasets_info():
    """
    Accepts a JSON body with:
      - user_id: the dados.gov user identifier to fetch datasets for
    """
    body = request.get_json(silent=True) or {}
    user_id = body.get("user_id")
    if not user_id:
        return jsonify({"error": "No user_id provided"}), 400

    task = dataset_fetch_tasks.fetch_user_datasets_info.s(user_id)
    task.set(task_id=str(uuid.uuid4()))

    redis_store.mark_job_issued(task.id, current_app.config["CELERY_RESULT_EXPIRES"])
    task.delay()

    return jsonify({
        "job_id": task.id,
        "status": "queued",
        "poll_url": f"/api/datasets_info_fetch_results/{task.id}"
    }), 202


@validation_bp.route("/datasets_info_fetch_results/<job_id>", methods=["GET"])
def datasets_info_fetch_results(job_id):
    if not redis_store.is_job_issued(job_id):
        return jsonify({"error": f"The {job_id} job_id is not associated with any dataset fetch job"}), 400

    result = celery.AsyncResult(job_id)

    if result.state == "PENDING":
        return jsonify({"job_id": job_id, "status": "queued"}), 202
    if result.state == "STARTED":
        return jsonify({"job_id": job_id, "status": "started"}), 202
    if result.state == "SUCCESS":
        return jsonify({"job_id": job_id, "status": "success", "result": result.result}), 200
    if result.state == "FAILURE":
        return jsonify({"job_id": job_id, "status": "failure", "error": str(result.result)}), 500

    return jsonify({"job_id": job_id, "status": result.state.lower()}), 202


# ============================================================
# Endpoints for preprocessing datasets

@validation_bp.route("/preprocess_upload_file", methods=["POST"])
def preprocess_upload_file():
    """
    Accepts a multipart/form-data request with:
      - file: the file to preprocess
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file_handler.is_allowed_file(file.filename, current_app.config["ALLOWED_EXTENSIONS"]):
        return jsonify({"error": "File type not allowed. Only .xlsx, .xls, and .csv are accepted."}), 400

    return _dispatch_preprocessing(file.filename, file.read())


@validation_bp.route("/preprocess_file_from_url", methods=["POST"])
def preprocess_file_from_url():
    """
    Accepts a JSON body with:
      - file_url: the URL of the file to fetch and preprocess
      - dadosgov_dataset_id: the dados.gov dataset identifier
      - dadosgov_resource_id: the dados.gov resource identifier
    """
    body = request.get_json(silent=True) or {}
    file_url = body.get("file_url")
    dadosgov_dataset_id = body.get("dadosgov_dataset_id")
    dadosgov_resource_id = body.get("dadosgov_resource_id")

    if not file_url:
        return jsonify({"error": "No file_url provided"}), 400
    if not dadosgov_dataset_id:
        return jsonify({"error": "No dadosgov_dataset_id provided"}), 400
    if not dadosgov_resource_id:
        return jsonify({"error": "No dadosgov_resource_id provided"}), 400

    file_name = file_url.split("/")[-1]
    if not file_handler.is_allowed_file(file_name, current_app.config["ALLOWED_EXTENSIONS"]):
        return jsonify({"error": "File type not allowed. Only .xlsx, .xls, and .csv are accepted."}), 400

    file_bytes = dadosgov_client.fetch_resource_file(file_url)

    return _dispatch_preprocessing(file_name, file_bytes, dadosgov_dataset_id, dadosgov_resource_id)


def _dispatch_preprocessing(file_name: str, file_bytes: bytes, dadosgov_dataset_id: str = None, dadosgov_resource_id: str = None):
    if dadosgov_resource_id:
        """
        This is done to avoid a mismatch between the resource ID and the dataframe ID, as the same resource may need to be 
        reprocessed when loading stored rules, and in this case the stored dataframe ID will match the resource ID.
        """
        unique_id = 'dataframe_' + dadosgov_dataset_id + '_' + dadosgov_resource_id
    else:
        unique_id = 'dataframe_' + str(uuid.uuid4().hex)

    dataframe_id, file_path = file_handler.save_upload_bytes(file_name, file_bytes, unique_id, current_app.config["UPLOAD_FOLDER"])

    task = preprocessing_tasks.preprocess_dataset.s(file_path, dataframe_id)
    task.set(task_id=str(uuid.uuid4()))

    report = PreprocessingReport(
        dadosgov_dataset_id=dadosgov_dataset_id,
        dadosgov_resource_id=dadosgov_resource_id,
        dataframe_id=dataframe_id,
        job_id=task.id,
        status=TaskStatus.QUEUED,
        original_filename=file_name
    )
    db.session.add(report)
    db.session.commit()

    task.delay()

    return jsonify({
        "job_id": task.id,
        "dataframe_id": dataframe_id,
        "preprocessing_report_id": report.id,
        "status": "queued",
        "poll_url": f"/api/results/{task.id}"
    }), 200


@validation_bp.route("/preprocessing_results/<job_id>", methods=["GET"])
def get_preprocessing_results(job_id):
    report: PreprocessingReport = PreprocessingReport.query.filter_by(job_id=job_id).first()

    if report is None:
        return jsonify({"error": f"The {job_id} job_id is not associated with any preprocessing results"}), 400
    if report.status == TaskStatus.QUEUED:
        return jsonify({"job_id": job_id, "status": "queued"}), 202
    if report.status == TaskStatus.STARTED:
        return jsonify({"job_id": job_id, "status": "started"}), 202
    if report.status == TaskStatus.SUCCESS:
        return jsonify({"job_id": job_id, "status": "success", "result": report.get_result()}), 200
    if report.status == TaskStatus.FAILURE:
        return jsonify({"job_id": job_id, "status": "failure", "error": report.error_message}), 500

    return jsonify({"job_id": job_id, "status": report.status.lower()}), 202


# ============================================================
# Endpoints for validating datasets

@validation_bp.route("/validate", methods=["POST"])
def validate():
    """
    Accepts a JSON body with:
      - datasets: an object mapping dataframe_ids to preprocessing_report_ids,
                  e.g. {"dataframe_id1": "preprocessing_report_id1", ...}
      - rules: an array of rule objects,
               e.g. [{"dataframe_ids": ["df1"], "type": "not_null", "column": "Age"}, ...]
    """
    body = request.get_json(silent=False)  # raises 400 with a real error if body is bad
    if not body:
        return jsonify({"error": "Request body must be JSON"}), 400

    datasets = body.get("datasets")
    if not datasets or not isinstance(datasets, dict):
        return jsonify({"error": "No datasets provided. Please preprocess datasets first."}), 400

    rules = body.get("rules")
    if not rules or not isinstance(rules, list) or len(rules) == 0:
        return jsonify({"error": "Rules must be a non-empty array"}), 400

    not_found_errors = []

    for dataframe_id in datasets.keys():
        if not dataframe_processing.is_dataframe_stored(dataframe_id):
            not_found_errors.append(f"Dataframe with ID {dataframe_id} not found. It may still be processing.")

    for preprocessing_report_id in datasets.values():
        try:
            report = PreprocessingReport.query.filter_by(id=preprocessing_report_id).first()
        except Exception as e:
            print(f"Error occurred while querying preprocessing report: {e}")
            report = None

        if report is None:
            not_found_errors.append(f"Preprocessing report with ID {preprocessing_report_id} not found. It may still be processing.")

    if not_found_errors:
        return jsonify({"error": ", ".join(not_found_errors)}), 400

    task = validation_task.run_validation.s(list(datasets.keys()), rules)
    task.set(task_id=str(uuid.uuid4()))

    report = ValidationReport(
        job_id=task.id,
        preprocessing_report_ids=list(datasets.values()),
        rules_applied=rules,
        status=TaskStatus.QUEUED
    )
    db.session.add(report)
    db.session.commit()
    task.delay()

    return jsonify({
        "job_id": task.id,
        "status": "queued",
        "poll_url": f"/api/results/{task.id}"
    }), 202


@validation_bp.route("/validation_results/<job_id>", methods=["GET"])
def get_validation_results(job_id):
    report: ValidationReport = ValidationReport.query.filter_by(job_id=job_id).first()

    if report is None:
        return jsonify({"error": f"The {job_id} job_id is not associated with any validation results"}), 400
    if report.status == TaskStatus.QUEUED:
        return jsonify({"job_id": job_id, "status": "queued"}), 202
    if report.status == TaskStatus.STARTED:
        return jsonify({"job_id": job_id, "status": "started"}), 202
    if report.status == TaskStatus.SUCCESS:
        return jsonify({"job_id": job_id, "status": "success", "result": report.get_result()}), 200
    if report.status == TaskStatus.FAILURE:
        return jsonify({"job_id": job_id, "status": "failure", "error": report.error_message}), 500

    return jsonify({"job_id": job_id, "status": report.status.lower()}), 202