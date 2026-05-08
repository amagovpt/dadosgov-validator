from flask import current_app
import logging
import time

from app import celery
from app.utils import dataset_processing, file_handler


@celery.task(name="dataset_store_tasks.preprocess_dataset", max_retries=3, default_retry_delay=5)
def preprocess_dataset(file_path: str, dataset_id: str):
    """
    Celery task to load a dataset into the in-memory store.

    Args:
        file_path: Absolute path to the file to be loaded
        dataset_id: The ID to associate with the loaded dataset
    """
    logging.info(f"Starting loading dataset from file into store with ID: {dataset_id}")
    start_time = time.time()
    df = dataset_processing.load_dataset_into_store(file_path, dataset_id)
    logging.info(f"Finished loading dataset {dataset_id} into store in {time.time() - start_time:.2f} seconds")

    file_handler.remove_file(file_path)  # Clean up the uploaded file immediately after loading into memory

    report = dict()

    logging.info(f"Starting preprocessing for dataset: {dataset_id}")
    start_time = time.time()
    report["presumed_column_types"] = dataset_processing.get_presumed_data_types(df)
    logging.info(f"Preprocessing completed for dataset: {dataset_id} in {time.time() - start_time:.2f} seconds")

    # Schedule deletion of the dataset after a set timeout to prevent memory bloat. 
    # This will only delete if the dataset is still stored (i.e. not already deleted by a previous validation run).
    remove_dataset_if_still_stored.apply_async(args=[dataset_id], countdown=current_app.config["DATASET_STORE_REMOVAL_TIMEOUT"])  

    return report

@celery.task(name="dataset_store_tasks.remove_dataset_if_still_stored", max_retries=3, default_retry_delay=5)
def remove_dataset_if_still_stored(dataset_id: str):
    """
    Celery task to delete a dataset from the in-memory store.

    Args:
        dataset_id: The ID of the dataset to be deleted
    """
    if dataset_processing.is_dataset_stored(dataset_id):
        dataset_processing.remove_dataset_from_store(dataset_id)
        logging.info(f"Dataset {dataset_id} removed from store after timeout")
    else:
        logging.info(f"Dataset {dataset_id} not found in store; no need to remove")