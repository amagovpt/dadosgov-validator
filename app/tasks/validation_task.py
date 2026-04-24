import os
import pandas as pd
from app import celery
from app.validators.engine import run_rules


@celery.task(bind=True)
def run_validation(self, file_path: str, rules: list) -> dict:
    """
    Celery task that:
      1. Loads the Excel file into a DataFrame
      2. Runs each rule against the DataFrame
      3. Returns a structured validation report
      4. Cleans up the uploaded file afterwards

    Args:
        file_path: Absolute path to the saved Excel file
        rules:     List of rule dicts, e.g. [{"type": "not_null", "column": "Age"}]

    Returns:
        A report dict with overall pass/fail and per-rule results
    """
    try:
        # Load the dataset
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format")

        # Run all rules through the validation engine
        report = run_rules(df, rules)

        return report

    except Exception as exc:
        # Retry up to 3 times with exponential backoff before marking as FAILURE
        raise self.retry(exc=exc, countdown=5, max_retries=3)

    finally:
        # Always clean up the temp file, whether the task succeeded or failed
        if os.path.exists(file_path):
            os.remove(file_path)
