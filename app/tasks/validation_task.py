import logging
import time

from app import celery
from app.validators.engine import run_rules
from app.utils import dataset_processing


@celery.task(name="validation_task.run_validation", max_retries=3, default_retry_delay=5)
def run_validation(dataset_id: str, rules: list) -> dict:
    """
    Celery task that:
      1. Loads the Excel file into a DataFrame
      2. Runs each rule against the DataFrame
      3. Returns a structured validation report
      4. Cleans up the uploaded file afterwards

    Args:
        dataset_id: The ID of the dataset to validate
        rules:     List of rule dicts, e.g. [{"type": "not_null", "column": "Age"}]

    Returns:
        A report dict with overall pass/fail and per-rule results
    """
    # Get the dataframe from the in-memory store using the dataset_id
    logging.info(f"Starting validation for dataset: {dataset_id} with rules: {rules}")

    start_time = time.time()
    df = dataset_processing.get_dataset_from_store(dataset_id)
    logging.info(f"Finished loading dataset {dataset_id} from store in {time.time() - start_time:.2f} seconds")
    
    # Run all rules through the validation engine
    logging.info(f"Running validation rules for dataset: {dataset_id}")
    start_time = time.time()
    report = run_rules(df, rules)
    logging.info(f"Finished validation for dataset {dataset_id} in {time.time() - start_time:.2f} seconds")

    return report

