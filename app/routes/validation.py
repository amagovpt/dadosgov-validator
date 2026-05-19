from flask import Blueprint, request, jsonify, current_app
import uuid
import json

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
        return jsonify({"error": f"The {job_id} job_id is not associated with any preprocessing results"}), 400

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
      - datasets: a JSON object mapping dataframe_ids to preprocessing_report_ids, e.g. {"dataframe_id1": "preprocessing_report_id1", "dataframe_id2": "preprocessing_report_id2"}
      - rules: a JSON array of rule objects

    Returns a job_id to poll for results.

    Example request (curl):
      curl -X POST http://localhost:5000/api/validate \
        -F "ed0f871e122d45adbd16f89d2e10545d" \
        -F 'rules=[{"type": "not_null", "column": "Age"}, {"type": "min_value", "column": "Score", "value": 0}]'
    """
    # --- Validate request ---
    datasets = request.args.get("datasets")
    if not datasets:
        return jsonify({"error": "No datasets parameter provided. Please preprocess datasets first."}), 400

    # Expect a JSON composed of {dataframe_id: preprocessing_report_id} pairs
    try:
        datasets = json.loads(datasets)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON in datasets parameter"}), 400

    not_found_errors = list()

    # Check if all provided dataframe_ids are stored and accessible
    for dataframe_id in datasets.keys():
        if not dataframe_processing.is_dataframe_stored(dataframe_id):
            not_found_errors.append(f"Dataframe with ID {dataframe_id} not found. It may still be processing.")
    
    # Check if all provided preprocessing_report_ids are stored and accessible
    for preprocessing_report_id in datasets.values():
        try:
            report = PreprocessingReport.query.filter_by(id=preprocessing_report_id).first()
        except Exception as e:
            print(f"Error occurred while querying preprocessing report: {e}")
            
        if report is None:
            not_found_errors.append(f"Preprocessing report with ID {preprocessing_report_id} not found. It may still be processing.")

    if len(not_found_errors) > 0:
        return jsonify({"error": ", ".join(not_found_errors)}), 400

    rules_raw = request.args.get("rules")
    if not rules_raw:
        return jsonify({"error": "No rules provided"}), 400

    try:
        rules = json.loads(rules_raw)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON in rules field"}), 400

    if not isinstance(rules, list) or len(rules) == 0:
        return jsonify({"error": "Rules must be a non-empty JSON array"}), 400

    # --- Running the task ---
    task = validation_task.run_validation.s(list(datasets.keys()), rules)
    task.set(task_id=str(uuid.uuid4()))

    report = ValidationReport(
        job_id=task.id,
        preprocessing_report_ids=list(datasets.values()), # store the list of preprocessing report IDs associated with this validation
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
        return jsonify({"error": f"The {job_id} job_id is not associated with any validation results"}), 400

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

