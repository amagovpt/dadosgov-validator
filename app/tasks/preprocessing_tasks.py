from flask import current_app
import logging
import time
from datetime import datetime

from app import celery, db
from app.utils import dataframe_processing, file_handler
from app.models import PreprocessingReport, TaskStatus


@celery.task(bind=True, name="dataset_store_tasks.preprocess_dataset", max_retries=3, default_retry_delay=5)
def preprocess_dataset(self, file_path: str, dataframe_id: str):
    """
    Celery task to load a dataset into the in-memory store.

    Args:
        file_path: Absolute path to the file to be loaded
        dataset_id: The ID to associate with the loaded dataset
    """
    # Mark as started
    report = PreprocessingReport.query.filter_by(job_id=self.request.id).first()
    report.status = TaskStatus.STARTED
    db.session.commit()

    try:
        logging.info(f"Starting loading dataframe from file into store with ID: {dataframe_id}")
        start_time = time.time()
        df = dataframe_processing.load_dataframe_into_store(file_path, dataframe_id)
        logging.info(f"Finished loading dataframe {dataframe_id} into store in {time.time() - start_time:.2f} seconds")

        file_handler.remove_file(file_path)  # Clean up the uploaded file immediately after loading into memory

        results = dict()

        logging.info(f"Starting preprocessing for dataframe: {dataframe_id}")
        start_time = time.time()
        results["column_names"] = dataframe_processing.get_column_names(df)
        results["presumed_column_types"] = dataframe_processing.get_presumed_data_types(df)
        logging.info(f"Preprocessing completed for dataframe: {dataframe_id} in {time.time() - start_time:.2f} seconds")

        # Schedule deletion of the dataframe after a set timeout to prevent memory bloat. 
        # This will only delete if the dataframe is still stored (i.e. not already deleted by a previous validation run).
        remove_dataframe_if_still_stored.apply_async(args=[dataframe_id], countdown=current_app.config["DATAFRAME_STORE_REMOVAL_TIMEOUT"])  

        # Mark as complete
        report.status = TaskStatus.SUCCESS
        report.column_names = results["column_names"]
        report.presumed_column_types = results["presumed_column_types"]
        report.completed_at = datetime.now()
        db.session.commit()
    except Exception as e:
        # Mark as failure
        db.session.rollback()
        report.status = TaskStatus.FAILURE
        report.error_message = str(e)
        report.completed_at = datetime.now()
        db.session.commit()
        raise

@celery.task(name="dataframe_store_tasks.remove_dataframe_if_still_stored", max_retries=3, default_retry_delay=5)
def remove_dataframe_if_still_stored(dataframe_id: str):
    """
    Celery task to delete a dataframe from the in-memory store.

    Args:
        dataframe_id: The ID of the dataframe to be deleted
    """
    if dataframe_processing.is_dataframe_stored(dataframe_id):
        dataframe_processing.remove_dataframe_from_store(dataframe_id)
        logging.info(f"Dataframe {dataframe_id} removed from store after timeout")
    else:
        logging.info(f"Dataframe {dataframe_id} not found in store; no need to remove")