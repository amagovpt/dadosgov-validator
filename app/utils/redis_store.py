import os
import pickle
import redis

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
client = redis.Redis.from_url(REDIS_URL)

def save_dataframe(key: str, df):
    """Serialize and store a DataFrame in Redis."""
    # Remove any existing entry for the key before saving the new dataframe
    client.delete(key)

    client.set(key, pickle.dumps(df))

def load_dataframe(key: str):
    """Retrieve and deserialize a DataFrame from Redis. Returns None if not found."""
    data = client.get(key)
    if data is None:
        return None
    return pickle.loads(data)

def delete_dataframe(key: str):
    """Remove a DataFrame from Redis."""
    client.delete(key)

def list_keys(pattern: str = '*'):
    """List all keys matching a pattern."""
    return [key.decode('utf-8') for key in client.keys(pattern)]

def is_dataframe_stored(key: str) -> bool:
    """Check if a DataFrame is stored under the given key."""
    return client.exists(key) == 1

def mark_job_issued(job_id: str, ttl_seconds: int):
    """
    Marks a job_id as issued, for tasks that have no DB-backed report row to
    check against. This lets a route distinguish "job_id we dispatched but
    Celery hasn't picked up yet" (PENDING) from "job_id that was never issued"
    (also reported as PENDING by Celery, since it has no other state).

    Args:
        job_id: The Celery task id that was dispatched.
        ttl_seconds: How long to remember this job_id for (should be >= the
            time the client is expected to keep polling for).
    """
    client.set(f"job_issued_{job_id}", 1, ex=ttl_seconds)

def is_job_issued(job_id: str) -> bool:
    """Checks whether the given job_id was previously marked via mark_job_issued."""
    return client.exists(f"job_issued_{job_id}") == 1