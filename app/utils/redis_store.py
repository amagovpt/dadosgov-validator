import os
import pickle
import redis

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
client = redis.Redis.from_url(REDIS_URL)

def save_dataframe(key: str, df):
    """Serialize and store a DataFrame in Redis."""
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