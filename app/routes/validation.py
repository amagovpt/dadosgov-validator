from flask import Blueprint, request, jsonify, current_app
from app.tasks import validation_task 
from app.tasks import preprocessing_tasks
from app.utils import dataset_processing
from app.utils import file_handler
from app.validators.descriptions import RULE_DESCRIPTIONS

validation_bp = Blueprint("validation", __name__)


@validation_bp.route("/available_rules", methods=["GET"])
def get_available_rules():
    """
    Returns a list of available validation rules.
    """
    return jsonify(RULE_DESCRIPTIONS), 200


@validation_bp.route("/tmp_get_current_dataset_store", methods=["GET"])
def get_current_dataset_store():
    """
    Temporary endpoint to inspect the current dataset store.
    """
    return jsonify(list(dataset_processing.list_stored_datasets())), 200


@validation_bp.route("/preprocess", methods=["POST"])
def preprocess():
    """
    Loads an uploaded file and preprocesses it.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file_handler.is_allowed_file(file.filename, current_app.config["ALLOWED_EXTENSIONS"]):
        return jsonify({"error": "File type not allowed. Only .xlsx, .xls, and .csv are accepted."}), 400
    
    dataset_id, file_path = file_handler.save_upload(file, current_app.config["UPLOAD_FOLDER"])

    task = preprocessing_tasks.preprocess_dataset.delay(file_path, dataset_id)

    return jsonify({
        "dataset_id": dataset_id,
        "job_id": task.id,
        "status": "queued",
        "poll_url": f"/api/results/{task.id}"
    }), 200


@validation_bp.route("/validate", methods=["POST"])
def validate():
    """
    Accepts a multipart/form-data request with:
      - dataset_id: the ID of the dataset to validate (must have been returned from /preprocess)
      - rules: a JSON array of rule objects

    Returns a job_id to poll for results.

    Example request (curl):
      curl -X POST http://localhost:5000/api/validate \
        -F "ed0f871e122d45adbd16f89d2e10545d" \
        -F 'rules=[{"type": "not_null", "column": "Age"}, {"type": "min_value", "column": "Score", "value": 0}]'
    """
    # --- Validate request ---
    dataset_id = request.args.get("dataset_id")
    if not dataset_id:
        return jsonify({"error": "No dataset_id provided. Please upload a file first to get a dataset_id."}), 400
    
    if not dataset_processing.is_dataset_stored(dataset_id):
        return jsonify({"error": f"Dataset with ID {dataset_id} not found. It may still be processing."}), 400

    rules_raw = request.args.get("rules")
    if not rules_raw:
        return jsonify({"error": "No rules provided"}), 400

    import json
    try:
        rules = json.loads(rules_raw)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON in rules field"}), 400

    if not isinstance(rules, list) or len(rules) == 0:
        return jsonify({"error": "Rules must be a non-empty JSON array"}), 400

    # --- Save file and dispatch task ---
    task = validation_task.run_validation.delay(dataset_id, rules)

    return jsonify({
        "job_id": task.id,
        "status": "queued",
        "poll_url": f"/api/results/{task.id}"
    }), 202


@validation_bp.route("/results/<job_id>", methods=["GET"])
def get_validation_results(job_id):
    """
    Poll this endpoint with the job_id returned from /validate.

    ATTENTION: Celery has a quick that it returns a "PENDING" state for job_ids that it doesn't recognize 
    (e.g. expired, wrong ID). So if you get "PENDING" for a long time, it likely means the job_id is 
    invalid or the result has expired from the Celery backend.

    Returns:
      - status: "queued" | "started" | "success" | "failure"
      - result: the validation report (only when status == "success")
      - error: error message (only when status == "failure")
    """
    from app import celery

    task = celery.AsyncResult(job_id)

    if task.state == "PENDING":
        return jsonify({"job_id": job_id, "status": "queued"}), 202

    if task.state == "STARTED":
        return jsonify({"job_id": job_id, "status": "started"}), 202

    if task.state == "SUCCESS":
        return jsonify({"job_id": job_id, "status": "success", "result": task.result}), 200

    if task.state == "FAILURE":
        return jsonify({"job_id": job_id, "status": "failure", "error": str(task.result)}), 500

    # Catch-all for any other Celery state (RETRY, REVOKED, etc.)
    return jsonify({"job_id": job_id, "status": task.state.lower()}), 202

