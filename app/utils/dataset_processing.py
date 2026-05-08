import pandas as pd
from app.utils import redis_store


def load_dataset_into_store(file_path: str, dataset_id: str) -> pd.DataFrame:
    """
    Loads an Excel or CSV file into the in-memory store as a DataFrame.

    Args:
        file_path: Absolute path to the file to be loaded
        dataset_id: The ID to associate with the loaded dataset
    """
    if file_path.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file_path)
    elif file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file type. Only .xlsx, .xls, and .csv are accepted.")
    
    redis_store.save_dataframe(dataset_id, df)
    return df

def get_dataset_from_store(dataset_id: str) -> pd.DataFrame:
    """
    Retrieves a dataset from the in-memory store.

    Args:
        dataset_id: The ID of the dataset to retrieve

    Returns:
        The DataFrame associated with the given dataset_id

    Raises:
        KeyError: If the dataset ID is not found in the store.
    """
    if redis_store.is_dataframe_stored(dataset_id):
        return redis_store.load_dataframe(dataset_id)

    raise KeyError(f"Dataset with ID {dataset_id} not found in store")

def remove_dataset_from_store(dataset_id: str):
    """
    Removes a dataset from the in-memory store. Doesn't check if it exists, just attempts to delete it.
    """
    redis_store.delete_dataframe(dataset_id)

def list_stored_datasets() -> list:
    """
    Lists all dataset IDs currently stored in the in-memory store.

    Returns:
        A list of dataset IDs currently stored.
    """
    return redis_store.list_keys()

def is_dataset_stored(dataset_id: str) -> bool:
    """
    Checks if a dataset with the given ID is currently stored in the in-memory store.

    Args:
        dataset_id: The ID of the dataset to check

    Returns:
        True if the dataset is stored, False otherwise.
    """
    return redis_store.is_dataframe_stored(dataset_id)

# Info retrieval functions for preprocessing report
DATATYPE_MAPPING = {
    'object': 'Não identificado',
    'str': 'Texto',
    'int64': 'Número inteiro',
    'float64': 'Número real',
    'bool': 'Sim ou não',
    'datetime64[ns]': 'Data e hora'
}

def get_column_names(df: pd.DataFrame) -> list:
    """
    Retrieves the column names of a stored dataset.

    Args:
        df: The DataFrame for which to retrieve column names

    Returns:
        A list of column names in the dataset.
    """
    return df.columns.tolist()

def get_presumed_data_types(df: pd.DataFrame) -> dict:
    """
    Retrieves the presumed data types of each column in a stored dataset.

    Args:
        df: The DataFrame for which to retrieve data types

    Returns:
        A dictionary mapping column names to their presumed data types.
    """
    dtypes_dict = df.dtypes.astype(str).to_dict()
    report = dict()
    for column, dtype in dtypes_dict.items():
        if dtype in DATATYPE_MAPPING:
            display_name = DATATYPE_MAPPING[dtype]
        else:
            display_name = 'Não identificado'
            
        report[column] = {'dtype_raw': dtype, 'display_name': display_name}

    return report