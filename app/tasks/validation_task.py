import logging
import time
from datetime import datetime

from app import celery, db
from app.validators.engine import run_rules
from app.utils import dataframe_processing
from app.models import ValidationReport, TaskStatus


@celery.task(bind=True, name="validation_task.run_validation", max_retries=3, default_retry_delay=5)
def run_validation(self, dataframe_ids: list[str], rules: list) -> dict:
    """
    Celery task that:
      1. Loads the Excel file into a DataFrame
      2. Runs each rule against the DataFrame
      3. Returns a structured validation report
      4. Cleans up the uploaded file afterwards

    Args:
        dataframe_ids: A list of IDs of the dataframes to use for validation
        rules:     List of rule dicts, e.g. [{"type": "not_null", "column": "Age"}]

    Returns:
        A report dict with overall pass/fail and per-rule results
    """
    report = ValidationReport.query.filter_by(job_id=self.request.id).first()
    report.status = TaskStatus.STARTED
    db.session.commit()

    try:
        # Get the dataframes from the in-memory store using the dataframe_ids
        logging.info(f"Starting validation for dataframes: {dataframe_ids} with rules: {rules}")

        start_time = time.time()
        df_store = {df_id: dataframe_processing.get_dataframe_from_store(df_id) for df_id in dataframe_ids}
        logging.info(f"Finished loading dataframes {dataframe_ids} from store in {time.time() - start_time:.2f} seconds")
        
        # Run all rules through the validation engine
        logging.info(f"Running validation rules for dataframes: {dataframe_ids}")
        start_time = time.time()
        results = run_rules(df_store, rules)
        logging.info(f"Finished validation for dataframes {dataframe_ids} in {time.time() - start_time:.2f} seconds")

        report.status = TaskStatus.SUCCESS
        report.report_result = results        # the full dict from run_rules()
        report.passed = results.get("passed") # top-level pass/fail from the result
        report.completed_at = datetime.now()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        report.status = TaskStatus.FAILURE
        report.error_message = str(e)
        report.completed_at = datetime.now()
        db.session.commit()
        raise

