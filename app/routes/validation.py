import os
from flask import Blueprint, request, jsonify, current_app
from app.tasks.validation_task import run_validation
from app.utils.file_handler import save_upload, is_allowed_file

validation_bp = Blueprint("validation", __name__)


@validation_bp.route("/validate", methods=["POST"])
def validate():
    """
    Accepts a multipart/form-data request with:
      - file: the Excel file to validate
      - rules: a JSON array of rule objects

    Returns a job_id to poll for results.

    Example request (curl):
      curl -X POST http://localhost:5000/api/validate \
        -F "file=@dataset.xlsx" \
        -F 'rules=[{"type": "not_null", "column": "Age"}, {"type": "min_value", "column": "Score", "value": 0}]'
    """
    # --- Validate request ---
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not is_allowed_file(file.filename, current_app.config["ALLOWED_EXTENSIONS"]):
        return jsonify({"error": "File type not allowed. Only .xlsx, .xls, and .csv are accepted."}), 400

    rules_raw = request.form.get("rules")
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
    file_path = save_upload(file, current_app.config["UPLOAD_FOLDER"])

    task = run_validation.delay(file_path, rules)

    return jsonify({
        "job_id": task.id,
        "status": "queued",
        "poll_url": f"/api/results/{task.id}"
    }), 202


@validation_bp.route("/results/<job_id>", methods=["GET"])
def get_results(job_id):
    """
    Poll this endpoint with the job_id returned from /validate.

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
