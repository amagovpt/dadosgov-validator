import logging

from app import celery
from app.services import dadosgov_client


@celery.task(name="dataset_fetch_tasks.fetch_user_datasets_info", max_retries=3, default_retry_delay=5)
def fetch_user_datasets_info(user_id: str) -> list[dict]:
    """
    Celery task to fetch the list of datasets associated with a user from the
    dados.gov API.

    Unlike the preprocessing/validation tasks, this result is NOT persisted to
    the database — it's only kept in Celery's result backend (Redis) until
    CELERY_RESULT_EXPIRES is reached. The route layer is expected to poll for
    the task's state/result directly (e.g. via AsyncResult), not via a DB-backed
    report model.

    Args:
        user_id: The dados.gov user identifier to fetch datasets for.

    Returns:
        A list of dataset dicts, see app.services.dadosgov_client for the shape.
    """
    logging.info(f"Starting fetch of datasets for user: {user_id}")
    datasets_info = dadosgov_client.fetch_datasets_for_user(user_id)
    logging.info(f"Finished fetching {len(datasets_info)} dataset(s) for user: {user_id}")

    return datasets_info