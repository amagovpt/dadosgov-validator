from flask import Blueprint, request, jsonify, current_app
import uuid

from app.tasks import validation_task 
from app.tasks import preprocessing_tasks
from app.utils import dataframe_processing
from app.utils import file_handler
from app.validators.descriptions import RULE_DESCRIPTIONS
from app import db
from app.models import PreprocessingReport, ValidationReport, TaskStatus

validation_bp = Blueprint("validation", __name__)


@validation_bp.route("/available_rules", methods=["GET"])
def get_available_rules():
    """
    Returns a list of available validation rules.
    """
    return jsonify(RULE_DESCRIPTIONS), 200


@validation_bp.route("/tmp_get_current_dataframe_store", methods=["GET"])
def get_current_dataframe_store():
    """
    Temporary endpoint to inspect the current dataframe store.
    """
    return jsonify(list(dataframe_processing.list_stored_dataframes())), 200


@validation_bp.route("/preprocess", methods=["POST"])
def preprocess():
    """
    Loads an uploaded file and preprocesses it.
    """
    # File validation
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file_handler.is_allowed_file(file.filename, current_app.config["ALLOWED_EXTENSIONS"]):
        return jsonify({"error": "File type not allowed. Only .xlsx, .xls, and .csv are accepted."}), 400
    
    # Dados.gov dataset id validation
    if "dadosgov_dataset_id" not in request.form:
        return jsonify({"error": "No dadosgov_dataset_id provided"}), 400
    
    dadosgov_dataset_id = request.form["dadosgov_dataset_id"]
    
    # Save file and dispatch preprocessing task
    dataframe_id, file_path = file_handler.save_upload(file, current_app.config["UPLOAD_FOLDER"])

    task = preprocessing_tasks.preprocess_dataset.s(file_path, dataframe_id)
    task.set(task_id=str(uuid.uuid4()))

    # DB interactions
    report = PreprocessingReport(
        dadosgov_dataset_id=dadosgov_dataset_id,
        dataframe_id=dataframe_id,
        job_id=task.id,
        status=TaskStatus.QUEUED,
        original_filename=file.filename
    )
    db.session.add(report)
    db.session.commit()

    # The job is first created and later run, as it need the report to be created on the DB before starting
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
    """
    Poll this endpoint with the job_id returned from /preprocess.

    Returns:
      - status: "queued" | "started" | "success" | "failure"
      - result: the validation report (only when status == "success")
      - error: error message (only when status == "failure")
    """
    report: PreprocessingReport = PreprocessingReport.query.filter_by(job_id=job_id).first()

    if report is None:
        return jsonify({"error": f"The {job_id} job_id is not associated with any results"}), 400

    if report.status == TaskStatus.QUEUED:
        return jsonify({"job_id": job_id, "status": "queued"}), 202

    if report.status == TaskStatus.STARTED:
        return jsonify({"job_id": job_id, "status": "started"}), 202

    if report.status == TaskStatus.SUCCESS:
        return jsonify({"job_id": job_id, "status": "success", "result": report.get_result()}), 200

    if report.status == TaskStatus.FAILURE:
        return jsonify({"job_id": job_id, "status": "failure", "error": report.error_message}), 500

    # Catch-all for any other Celery state (RETRY, REVOKED, etc.)
    return jsonify({"job_id": job_id, "status": report.status.lower()}), 202


@validation_bp.route("/validate", methods=["POST"])
def validate():
    """
    Accepts a multipart/form-data request with:
      - dataframe_id: the ID of the dataframe to validate (must have been returned from /preprocess)
      - rules: a JSON array of rule objects

    Returns a job_id to poll for results.

    Example request (curl):
      curl -X POST http://localhost:5000/api/validate \
        -F "ed0f871e122d45adbd16f89d2e10545d" \
        -F 'rules=[{"type": "not_null", "column": "Age"}, {"type": "min_value", "column": "Score", "value": 0}]'
    """
    # --- Validate request ---
    dataframe_id = request.args.get("dataframe_id")
    if not dataframe_id:
        return jsonify({"error": "No dataframe_id provided. Please upload a file first to get a dataframe_id."}), 400

    if not dataframe_processing.is_dataframe_stored(dataframe_id):
        return jsonify({"error": f"Dataframe with ID {dataframe_id} not found. It may still be processing."}), 400

    rules_raw = request.args.get("rules")
    if not rules_raw:
        return jsonify({"error": "No rules provided"}), 400
    
    preprocessing_job_id = request.args.get("preprocessing_job_id")
    if not preprocessing_job_id:
        return jsonify({"error": "No preprocessing_job_id provided."})
    
    preprocessing_report = PreprocessingReport.query.filter_by(
        id=preprocessing_job_id
    ).first()
    if preprocessing_report is None:
        return jsonify({"error": "The preprocessing_job_id provided doesn't match any preprocessing report stored."})

    import json
    try:
        rules = json.loads(rules_raw)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON in rules field"}), 400

    if not isinstance(rules, list) or len(rules) == 0:
        return jsonify({"error": "Rules must be a non-empty JSON array"}), 400

    # --- Running the task ---
    task = validation_task.run_validation.s(dataframe_id, rules)
    task.set(task_id=str(uuid.uuid4()))

    report = ValidationReport(
        job_id=task.id,
        preprocessing_report_id=preprocessing_report.id,
        rules_applied=rules,
        status=TaskStatus.QUEUED
    )
    db.session.add(report)
    db.session.commit()

    # The job is first created and later run, as it need the report to be created on the DB before starting
    task.delay()

    return jsonify({
        "job_id": task.id,
        "status": "queued",
        "poll_url": f"/api/results/{task.id}"
    }), 202


@validation_bp.route("/validation_results/<job_id>", methods=["GET"])
def get_validation_results(job_id):
    """
    Poll this endpoint with the job_id returned from /validate.

    Returns:
      - status: "queued" | "started" | "success" | "failure"
      - result: the validation report (only when status == "success")
      - error: error message (only when status == "failure")
    """
    report: ValidationReport = ValidationReport.query.filter_by(job_id=job_id).first()

    if report is None:
        return jsonify({"error": f"The {job_id} job_id is not associated with any results"}), 400

    if report.status == TaskStatus.QUEUED:
        return jsonify({"job_id": job_id, "status": "queued"}), 202

    if report.status == TaskStatus.STARTED:
        return jsonify({"job_id": job_id, "status": "started"}), 202

    if report.status == TaskStatus.SUCCESS:
        return jsonify({"job_id": job_id, "status": "success", "result": report.get_result()}), 200

    if report.status == TaskStatus.FAILURE:
        return jsonify({"job_id": job_id, "status": "failure", "error": report.error_message}), 500

    # Catch-all for any other Celery state (RETRY, REVOKED, etc.)
    return jsonify({"job_id": job_id, "status": report.status.lower()}), 202

