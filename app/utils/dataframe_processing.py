import pandas as pd
from app.utils import redis_store


def load_dataframe_into_store(file_path: str, dataframe_id: str) -> pd.DataFrame:
    """
    Loads an Excel or CSV file into the in-memory store as a DataFrame.

    Args:
        file_path: Absolute path to the file to be loaded
        dataframe_id: The ID to associate with the loaded dataframe
    """
    if file_path.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file_path)
    elif file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file type. Only .xlsx, .xls, and .csv are accepted.")
    
    redis_store.save_dataframe(dataframe_id, df)
    return df

def get_dataframe_from_store(dataframe_id: str) -> pd.DataFrame:
    """
    Retrieves a dataframe from the in-memory store.

    Args:
        dataframe_id: The ID of the dataframe to retrieve

    Returns:
        The DataFrame associated with the given dataframe_id

    Raises:
        KeyError: If the dataframe ID is not found in the store.
    """
    if redis_store.is_dataframe_stored(dataframe_id):
        return redis_store.load_dataframe(dataframe_id)

    raise KeyError(f"Dataframe with ID {dataframe_id} not found in store")

def remove_dataframe_from_store(dataframe_id: str):
    """
    Removes a dataframe from the in-memory store. Doesn't check if it exists, just attempts to delete it.
    """
    redis_store.delete_dataframe(dataframe_id)

def list_stored_dataframes() -> list:
    """
    Lists all dataframe IDs currently stored in the in-memory store.

    Returns:
        A list of dataframe IDs currently stored.
    """
    return [key for key in redis_store.list_keys() if key.startswith("dataframe_")]

def is_dataframe_stored(dataframe_id: str) -> bool:
    """
    Checks if a dataframe with the given ID is currently stored in the in-memory store.

    Args:
        dataframe_id: The ID of the dataframe to check

    Returns:
        True if the dataframe is stored, False otherwise.
    """
    return redis_store.is_dataframe_stored(dataframe_id)

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
    Retrieves the column names of a stored dataframe.

    Args:
        df: The DataFrame for which to retrieve column names

    Returns:
        A list of column names in the dataframe.
    """
    return df.columns.tolist()

def get_presumed_data_types(df: pd.DataFrame) -> dict:
    """
    Retrieves the presumed data types of each column in a stored dataframe.

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