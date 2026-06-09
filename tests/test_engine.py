"""
Basic tests for the validation engine.
Run with 'python -m pytest' on the root folder.
"""

import pandas as pd
import pytest
import uuid
import json
from app.validators.engine import run_rules
from app.utils import redis_store


@pytest.fixture
def test_not_null_df():
    return pd.DataFrame({
        "ID":     [1, 2, 2, 4],
        "Name":   ["Alice", "Bob", None, "Diana"],
        "Score":  [85, -5, 95, 110],
        "Status": ["active", "inactive", "active", "banned"],
    })

@pytest.fixture
def test_unique_generic_df():
    return pd.DataFrame({
        "a": [1, 2, 3, 4],
        "b": ["x", "x", "x", "x"],
        "c": [10, 20, 30, 40]
    })

@pytest.fixture
def test_generic_length_df():
    return pd.DataFrame({
        "Text": ["short", "medium length", "a very long string, this is, indeed is, a very long long string", None, "exactly 17 chars!"],
        "Numbers": [123, 4.567, 890.12, 3456782, 9012.345]
    })

@pytest.fixture
def test_length_exact_df():
    return pd.DataFrame({
        "Text": ["abcd", "efgh", "ijkl", None],
        "Numbers": [1.234, 12.34, 123.4, 1234]
    })

@pytest.fixture
def test_possible_values_df():
    return pd.DataFrame({
        "Status": ["a", "b", "c", None, "d"]
    })

@pytest.fixture
def test_percentage_max_decimal_places_df():
    return pd.DataFrame({
        "Percentage": [2, 189, 0.123, 0.1234, 0.12, None, 0.12345]
    })

@pytest.fixture
def test_domains_numeric_df():
    return pd.DataFrame({
        "Value": [85, -5, 95, 110]
    })

@pytest.fixture
def test_one_to_one_columns_passes_df():
    return pd.DataFrame({
        'Codigo': ['A', 'B', 'C', 'D', 'E'],
        'Descricao': ['Descricao A', 'Descricao B', 'Descricao C', 'Descricao D', 'Descricao E'],
    })

@pytest.fixture
def test_one_to_one_columns_fails_df():
    return pd.DataFrame({
        'Codigo': ['A', 'B', 'C', 'C', 'E'],
        'Descricao': ['Descricao A', 'Descricao A', 'Descricao C', 'Descricao D', 'Descricao E'],
    })

@pytest.fixture
def test_boundaries_extended_table_coherence_passes_dfs():
    return (
        pd.DataFrame({
            "BaseValue": ['a', 'a', 'b', None]
        }),
        pd.DataFrame({
            "ExtendedValue1": ['a', 'b', 'b', None],
            "ExtendedValue2": ['a', 'b', 'X', None]
        })
    )

@pytest.fixture
def test_boundaries_extended_table_coherence_fails_dfs():
    return (
        pd.DataFrame({
            "BaseValue": ['a', 'a', 'b', None]
        }),
        pd.DataFrame({
            "ExtendedValue": ['a', 'c', 'c', None]
        })
    )

@pytest.fixture
def test_domains_only_one_value_across_datasets_passes_dfs():
        return (
        pd.DataFrame({
            "BaseValue": ['a', 'a', 'a', None]
        }),
        pd.DataFrame({
            "ExtendedValue1": ['a', None, 'a'],
            "ExtendedValue2": ['a', 'a', None]
        })
    )

@pytest.fixture
def test_domains_only_one_value_across_datasets_fails_1_dfs():
    return (
        pd.DataFrame({
            "BaseValue": ['a', 'a', 'b', None]
        }),
        pd.DataFrame({
            "ExtendedValue1": ['a', None, 'a'],
            "ExtendedValue2": ['a', 'a', None]
        })
    )

@pytest.fixture
def test_domains_only_one_value_across_datasets_fails_2_dfs():
    return (
        pd.DataFrame({
            "BaseValue": ['a', 'a', 'a', None]
        }),
        pd.DataFrame({
            "ExtendedValue1": ['a', None, 'a'],
            "ExtendedValue2": ['a', 'b', None]
        })
    )

@pytest.fixture
def test_format_no_leading_whitespace_passes_df():
    return pd.DataFrame({
        "Value": ["a", "b", "c", None]
    })

@pytest.fixture
def test_format_no_leading_whitespace_fails_1_df():
    return pd.DataFrame({
        "Value": [" a", "b", "c", None]
    })

@pytest.fixture
def test_format_no_leading_whitespace_fails_2_df():
    return pd.DataFrame({
        "Value": [" a", "\tb", "c", None]
    })

@pytest.fixture
def test_domain_not_zero_passes_df():
    return pd.DataFrame({
        "Value": ['abc', 1, 4, None]
    })

@pytest.fixture
def test_domain_not_zero_fails_1_df():
    return pd.DataFrame({
        "Value": ['abc', 1, '0.0', None]
    })

@pytest.fixture
def test_domain_not_zero_fails_2_df():
    return pd.DataFrame({
        "Value": ['abc', 1, 0, None]
    })

@pytest.fixture
def test_boundaries_not_all_values_the_same_passes_df():
    return pd.DataFrame({
        "Value": ['a', 'b', None, 'b']
    })

@pytest.fixture
def test_boundaries_not_all_values_the_same_fails_df():
    return pd.DataFrame({
        "Value": ['b', 'b', None, 'b']
    })

@pytest.fixture
def test_boundaries_sum_equals_passes_df():
    return pd.DataFrame({
        "Value": [10, 20, 10, None, 10]
    })

@pytest.fixture
def test_boundaries_sum_equals_fails_1_df():
    return pd.DataFrame({
        "Value": ['a', 10, 20, None, 10]
    })

@pytest.fixture
def test_boundaries_sum_equals_fails_2_df():
    return pd.DataFrame({
        "Value": [10, 20, 10, None, 10]
    })

# -------------------- TEST NOT NULL --------------------
def test_not_null_passes(test_not_null_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_not_null_df)
    
    rules = [{"dataframe_ids": [df_id], "type": "test_not_null", "column": "ID"}]
    report = run_rules({df_id: test_not_null_df}, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 1, json.dumps(report, indent=4)
    assert report["failed"] == 0, json.dumps(report, indent=4)

def test_not_null_fails(test_not_null_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_not_null_df)

    rules = [{"dataframe_ids": [df_id], "type": "test_not_null", "column": "Name"}]
    report = run_rules({df_id: test_not_null_df}, rules)
    redis_store.delete_dataframe(df_id)
    
    assert report["failed"] == 1, json.dumps(report, indent=4)
    assert report["results"][0]["failures"][0]["row"] == 2, json.dumps(report, indent=4)

# -------------------- TEST UNIQUE GENERIC --------------------
def test_unique_generic_passes_1(test_unique_generic_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_unique_generic_df)

    rules = [{"dataframe_ids": [df_id], "type": "test_unique_generic", "columns": ["a"]}]
    report = run_rules({df_id: test_unique_generic_df}, rules)
    redis_store.delete_dataframe(df_id)
    
    assert report["passed"] == 1, json.dumps(report, indent=4)
    assert report["failed"] == 0, json.dumps(report, indent=4)

def test_unique_generic_passes_2(test_unique_generic_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_unique_generic_df)

    rules = [{"dataframe_ids": [df_id], "type": "test_unique_generic", "columns": ["b", "c"]}]
    report = run_rules({df_id: test_unique_generic_df}, rules)
    redis_store.delete_dataframe(df_id)
    
    assert report["passed"] == 1, json.dumps(report, indent=4)
    assert report["failed"] == 0, json.dumps(report, indent=4)

def test_unique_generic_fails(test_unique_generic_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_unique_generic_df)

    rules = [{"dataframe_ids": [df_id], "type": "test_unique_generic", "columns": ["b"]}]
    report = run_rules({df_id: test_unique_generic_df}, rules)
    redis_store.delete_dataframe(df_id)
    
    assert report["failed"] == 1, json.dumps(report, indent=4)
    assert len(report["results"][0]["failures"]) == 4, json.dumps(report, indent=4)

# -------------------- TEST LENGTH MAX --------------------
def test_length_max_passes(test_generic_length_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_generic_length_df)

    rules = [
        {"dataframe_ids": [df_id], "type": "test_length_max", "column": "Text", "max_length": 63},
        {"dataframe_ids": [df_id], "type": "test_length_max", "column": "Numbers", "max_length": 7}
    ]
    report = run_rules({df_id: test_generic_length_df}, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 2, json.dumps(report, indent=4)
    assert report["failed"] == 0, json.dumps(report, indent=4)

def test_length_max_fails(test_generic_length_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_generic_length_df)

    rules = [
        {"dataframe_ids": [df_id], "type": "test_length_max", "column": "Text", "max_length": 13},
        {"dataframe_ids": [df_id], "type": "test_length_max", "column": "Numbers", "max_length": 5}
    ]
    report = run_rules({df_id: test_generic_length_df}, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 0, json.dumps(report, indent=4)
    assert report["failed"] == 2, json.dumps(report, indent=4)
    assert len(report["results"][0]["failures"]) == 2, json.dumps(report, indent=4)
    assert len(report["results"][1]["failures"]) == 2, json.dumps(report, indent=4)

# -------------------- TEST LENGTH MIN --------------------
def test_length_min_passes(test_generic_length_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_generic_length_df)

    rules = [
        {"dataframe_ids": [df_id], "type": "test_length_min", "column": "Text", "min_length": 5},
        {"dataframe_ids": [df_id], "type": "test_length_min", "column": "Numbers", "min_length": 3}
    ]
    report = run_rules({df_id: test_generic_length_df}, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 2, json.dumps(report, indent=4)
    assert report["failed"] == 0, json.dumps(report, indent=4)

def test_length_min_fails(test_generic_length_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_generic_length_df)

    rules = [
        {"dataframe_ids": [df_id], "type": "test_length_min", "column": "Text", "min_length": 10},
        {"dataframe_ids": [df_id], "type": "test_length_min", "column": "Numbers", "min_length": 6}
    ]
    report = run_rules({df_id: test_generic_length_df}, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 0, json.dumps(report, indent=4)
    assert report["failed"] == 2, json.dumps(report, indent=4)
    assert len(report["results"][0]["failures"]) == 1, json.dumps(report, indent=4)
    assert len(report["results"][1]["failures"]) == 3, json.dumps(report, indent=4)

# -------------------- TEST LENGTH EXACT --------------------
def test_length_exact_passes(test_length_exact_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_length_exact_df)

    rules = [
        {"dataframe_ids": [df_id], "type": "test_length_exact", "column": "Text", "exact_length": 4},
        {"dataframe_ids": [df_id], "type": "test_length_exact", "column": "Numbers", "exact_length": 4}
    ]
    report = run_rules({df_id: test_length_exact_df}, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 2, json.dumps(report, indent=4)
    assert report["failed"] == 0, json.dumps(report, indent=4)

def test_length_exact_fails(test_length_exact_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_length_exact_df)

    rules = [
        {"dataframe_ids": [df_id], "type": "test_length_exact", "column": "Text", "exact_length": 5},
        {"dataframe_ids": [df_id], "type": "test_length_exact", "column": "Numbers", "exact_length": 5}
    ]
    report = run_rules({df_id: test_length_exact_df}, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 0, json.dumps(report, indent=4)
    assert report["failed"] == 2, json.dumps(report, indent=4)
    assert len(report["results"][0]["failures"]) == 3, json.dumps(report, indent=4)
    assert len(report["results"][1]["failures"]) == 4, json.dumps(report, indent=4)

# -------------------- TEST POSSIBLE VALUES --------------------
def test_possible_values_passes(test_possible_values_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_possible_values_df)

    rules = [{"dataframe_ids": [df_id], "type": "test_possible_values", "column": "Status", "possible_values": ["a", "b", "c", "d"]}]
    report = run_rules({df_id: test_possible_values_df}, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 1, json.dumps(report, indent=4)
    assert report["failed"] == 0, json.dumps(report, indent=4)

def test_possible_values_fails(test_possible_values_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_possible_values_df)

    rules = [{"dataframe_ids": [df_id], "type": "test_possible_values", "column": "Status", "possible_values": ["a", "b"]}]
    report = run_rules({df_id: test_possible_values_df}, rules)
    redis_store.delete_dataframe(df_id)
    
    assert report["failed"] == 1, json.dumps(report, indent=4)
    assert len(report["results"][0]["failures"]) == 2, json.dumps(report, indent=4)

# -------------------- TEST PERCENTAGE MAX DECIMAL PLACES --------------------
def test_percentage_max_decimal_places_passes(test_percentage_max_decimal_places_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_percentage_max_decimal_places_df)

    rules = [{"dataframe_ids": [df_id], "type": "test_percentage_max_decimal_places", "column": "Percentage", "max_decimal_places": 5}]
    report = run_rules({df_id: test_percentage_max_decimal_places_df}, rules)
    redis_store.delete_dataframe(df_id)
    
    assert report["passed"] == 1, json.dumps(report, indent=4)
    assert report["failed"] == 0, json.dumps(report, indent=4)

def test_percentage_max_decimal_places_fails(test_percentage_max_decimal_places_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_percentage_max_decimal_places_df)

    rules = [{"dataframe_ids": [df_id], "type": "test_percentage_max_decimal_places", "column": "Percentage", "max_decimal_places": 3}]
    report = run_rules({df_id: test_percentage_max_decimal_places_df}, rules)
    redis_store.delete_dataframe(df_id)
    
    assert report["failed"] == 1, json.dumps(report, indent=4)
    assert len(report["results"][0]["failures"]) == 2, json.dumps(report, indent=4)

# -------------------- TEST DOMAINS NUMERIC --------------------
def test_domains_numeric_passes_1(test_domains_numeric_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_domains_numeric_df)

    rules = [{"dataframe_ids": [df_id], "type": "test_domains_numeric", "column": "Value", "min_value": -10}]
    report = run_rules({df_id: test_domains_numeric_df}, rules)
    redis_store.delete_dataframe(df_id)
    
    assert report["passed"] == 1, json.dumps(report, indent=4)
    assert report["failed"] == 0, json.dumps(report, indent=4)

def test_domains_numeric_passes_2(test_domains_numeric_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_domains_numeric_df)

    rules = [{"dataframe_ids": [df_id], "type": "test_domains_numeric", "column": "Value", "max_value": 200}]
    report = run_rules({df_id: test_domains_numeric_df}, rules)
    redis_store.delete_dataframe(df_id)
    
    assert report["passed"] == 1, json.dumps(report, indent=4)
    assert report["failed"] == 0, json.dumps(report, indent=4)

def test_domains_numeric_passes_3(test_domains_numeric_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_domains_numeric_df)

    rules = [{"dataframe_ids": [df_id], "type": "test_domains_numeric", "column": "Value", "min_value": -10, "max_value": 200}]
    report = run_rules({df_id: test_domains_numeric_df}, rules)
    redis_store.delete_dataframe(df_id)
    
    assert report["passed"] == 1, json.dumps(report, indent=4)
    assert report["failed"] == 0, json.dumps(report, indent=4)

def test_domains_numeric_fails_1(test_domains_numeric_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_domains_numeric_df)

    rules = [{"dataframe_ids": [df_id], "type": "test_domains_numeric", "column": "Value", "min_value": 0}]
    report = run_rules({df_id: test_domains_numeric_df}, rules)
    redis_store.delete_dataframe(df_id)

    assert report["failed"] == 1, json.dumps(report, indent=4)
    assert len(report["results"][0]["failures"]) == 1, json.dumps(report, indent=4)

def test_domains_numeric_fails_2(test_domains_numeric_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_domains_numeric_df)

    rules = [{"dataframe_ids": [df_id], "type": "test_domains_numeric", "column": "Value", "max_value": 90}]
    report = run_rules({df_id: test_domains_numeric_df}, rules)
    redis_store.delete_dataframe(df_id)

    assert report["failed"] == 1, json.dumps(report, indent=4)
    assert len(report["results"][0]["failures"]) == 2, json.dumps(report, indent=4)

def test_domains_numeric_fails_3(test_domains_numeric_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_domains_numeric_df)

    rules = [{"dataframe_ids": [df_id], "type": "test_domains_numeric", "column": "Value", "min_value": 0, "max_value": 90}]
    report = run_rules({df_id: test_domains_numeric_df}, rules)
    redis_store.delete_dataframe(df_id)

    assert report["failed"] == 1, json.dumps(report, indent=4)
    assert len(report["results"][0]["failures"]) == 3, json.dumps(report, indent=4)

# -------------------- TEST ONE TO ONE COLUMNS --------------------
def test_one_to_one_columns_passes(test_one_to_one_columns_passes_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_one_to_one_columns_passes_df)

    rules = [{"dataframe_ids": [df_id], "type": "test_one_to_one_columns", "column1": "Codigo", "column2": "Descricao"}]
    report = run_rules({df_id: test_one_to_one_columns_passes_df}, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 1, json.dumps(report, indent=4)
    assert report["failed"] == 0, json.dumps(report, indent=4)

def test_one_to_one_columns_fails(test_one_to_one_columns_fails_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_one_to_one_columns_fails_df)

    rules = [{"dataframe_ids": [df_id], "type": "test_one_to_one_columns", "column1": "Codigo", "column2": "Descricao"}]
    report = run_rules({df_id: test_one_to_one_columns_fails_df}, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 0, json.dumps(report, indent=4)
    assert report["failed"] == 1, json.dumps(report, indent=4)

# -------------------- TEST BOUNDARIES EXTENDED TABLE COHERENCE --------------------
def test_boundaries_extended_table_coherence_passes(test_boundaries_extended_table_coherence_passes_dfs):
    df_base_id = f"dataframe_{str(uuid.uuid4())}"
    df_extended_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_base_id, test_boundaries_extended_table_coherence_passes_dfs[0])
    redis_store.save_dataframe(df_extended_id, test_boundaries_extended_table_coherence_passes_dfs[1])

    rules = [
        {
            "dataframe_ids": [df_base_id, df_extended_id], 
            "type": "test_boundaries_extended_table_coherence", 
            "base_column": "BaseValue", 
            "extended_column": "ExtendedValue1"
        },
        {
            "dataframe_ids": [df_base_id, df_extended_id], 
            "type": "test_boundaries_extended_table_coherence", 
            "base_column": "BaseValue", 
            "extended_column": "ExtendedValue2"
        }
    ]
    df_store = {
        df_base_id: test_boundaries_extended_table_coherence_passes_dfs[0], 
        df_extended_id: test_boundaries_extended_table_coherence_passes_dfs[1]
    }
    report = run_rules(df_store, rules)
    redis_store.delete_dataframe(df_base_id)
    redis_store.delete_dataframe(df_extended_id)

    assert report["passed"] == 2, json.dumps(report, indent=4)
    assert report["failed"] == 0, json.dumps(report, indent=4)

def test_boundaries_extended_table_coherence_fails(test_boundaries_extended_table_coherence_fails_dfs):
    df_base_id = f"dataframe_{str(uuid.uuid4())}"
    df_extended_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_base_id, test_boundaries_extended_table_coherence_fails_dfs[0])
    redis_store.save_dataframe(df_extended_id, test_boundaries_extended_table_coherence_fails_dfs[1])

    rules = [
        {
            "dataframe_ids": [df_base_id, df_extended_id], 
            "type": "test_boundaries_extended_table_coherence", 
            "base_column": "BaseValue", 
            "extended_column": "ExtendedValue"
        }
    ]
    df_store = {
        df_base_id: test_boundaries_extended_table_coherence_fails_dfs[0], 
        df_extended_id: test_boundaries_extended_table_coherence_fails_dfs[1]
    }
    report = run_rules(df_store, rules)
    redis_store.delete_dataframe(df_base_id)
    redis_store.delete_dataframe(df_extended_id)

    assert report["passed"] == 0, json.dumps(report, indent=4)
    assert report["failed"] == 1, json.dumps(report, indent=4)

# -------------------- TEST DOMAINS ONLY ONE VALUE ACCROSS DATASETS --------------------
def test_domains_only_one_value_across_datasets_passes(test_domains_only_one_value_across_datasets_passes_dfs):
    df_base_id = f"dataframe_{str(uuid.uuid4())}"
    df_extended_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_base_id, test_domains_only_one_value_across_datasets_passes_dfs[0])
    redis_store.save_dataframe(df_extended_id, test_domains_only_one_value_across_datasets_passes_dfs[1])

    # Using the same extended DataFrame twice
    rules = [
        {
            "dataframe_ids": [df_base_id, df_extended_id, df_extended_id],
            "type": "test_domains_only_one_value_across_datasets",
            "base_column": "BaseValue",
            "extended_columns": ["ExtendedValue1", "ExtendedValue2"]
        }
    ]
    df_store = {
        df_base_id: test_domains_only_one_value_across_datasets_passes_dfs[0], 
        df_extended_id: test_domains_only_one_value_across_datasets_passes_dfs[1]
    }
    report = run_rules(df_store, rules)
    redis_store.delete_dataframe(df_base_id)
    redis_store.delete_dataframe(df_extended_id)

    assert report["passed"] == 1, json.dumps(report, indent=4)
    assert report["failed"] == 0, json.dumps(report, indent=4)

def test_domains_only_one_value_across_datasets_fails_1(test_domains_only_one_value_across_datasets_fails_1_dfs):
    df_base_id = f"dataframe_{str(uuid.uuid4())}"
    df_extended_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_base_id, test_domains_only_one_value_across_datasets_fails_1_dfs[0])
    redis_store.save_dataframe(df_extended_id, test_domains_only_one_value_across_datasets_fails_1_dfs[1])

    # Using the same extended DataFrame twice
    rules = [
        {
            "dataframe_ids": [df_base_id, df_extended_id, df_extended_id],
            "type": "test_domains_only_one_value_across_datasets",
            "base_column": "BaseValue",
            "extended_columns": ["ExtendedValue1", "ExtendedValue2"]
        }
    ]
    df_store = {
        df_base_id: test_domains_only_one_value_across_datasets_fails_1_dfs[0], 
        df_extended_id: test_domains_only_one_value_across_datasets_fails_1_dfs[1]
    }
    report = run_rules(df_store, rules)
    redis_store.delete_dataframe(df_base_id)
    redis_store.delete_dataframe(df_extended_id)

    assert report["passed"] == 0, json.dumps(report, indent=4)
    assert report["failed"] == 1, json.dumps(report, indent=4)

def test_domains_only_one_value_across_datasets_fails_1(test_domains_only_one_value_across_datasets_fails_2_dfs):
    df_base_id = f"dataframe_{str(uuid.uuid4())}"
    df_extended_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_base_id, test_domains_only_one_value_across_datasets_fails_2_dfs[0])
    redis_store.save_dataframe(df_extended_id, test_domains_only_one_value_across_datasets_fails_2_dfs[1])

    # Using the same extended DataFrame twice
    rules = [
        {
            "dataframe_ids": [df_base_id, df_extended_id, df_extended_id],
            "type": "test_domains_only_one_value_across_datasets",
            "base_column": "BaseValue",
            "extended_columns": ["ExtendedValue1", "ExtendedValue2"]
        }
    ]
    df_store = {
        df_base_id: test_domains_only_one_value_across_datasets_fails_2_dfs[0], 
        df_extended_id: test_domains_only_one_value_across_datasets_fails_2_dfs[1]
    }
    report = run_rules(df_store, rules)
    redis_store.delete_dataframe(df_base_id)
    redis_store.delete_dataframe(df_extended_id)

    assert report["passed"] == 0, json.dumps(report, indent=4)
    assert report["failed"] == 1, json.dumps(report, indent=4)

# -------------------- TEST FORMAT NO LEADING WHITESPACE --------------------
def test_format_no_leading_whitespace_passes(test_format_no_leading_whitespace_passes_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_format_no_leading_whitespace_passes_df)

    rules = [
        {
            "dataframe_ids": [df_id],
            "type": "test_format_no_leading_whitespace",
            "column": "Value"
        }
    ]
    df_store = {df_id: test_format_no_leading_whitespace_passes_df}
    report = run_rules(df_store, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 1, json.dumps(report, indent=4)
    assert report["failed"] == 0, json.dumps(report, indent=4)

def test_format_no_leading_whitespace_fails_1(test_format_no_leading_whitespace_fails_1_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_format_no_leading_whitespace_fails_1_df)

    rules = [
        {
            "dataframe_ids": [df_id],
            "type": "test_format_no_leading_whitespace",
            "column": "Value"
        }
    ]
    df_store = {df_id: test_format_no_leading_whitespace_fails_1_df}
    report = run_rules(df_store, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 0, json.dumps(report, indent=4)
    assert report["failed"] == 1, json.dumps(report, indent=4)

def test_format_no_leading_whitespace_fails_2(test_format_no_leading_whitespace_fails_2_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_format_no_leading_whitespace_fails_2_df)

    rules = [
        {
            "dataframe_ids": [df_id],
            "type": "test_format_no_leading_whitespace",
            "column": "Value"
        }
    ]
    df_store = {df_id: test_format_no_leading_whitespace_fails_2_df}
    report = run_rules(df_store, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 0, json.dumps(report, indent=4)
    assert report["failed"] == 1, json.dumps(report, indent=4)

# -------------------- TEST FORMAT NOT ZERO --------------------
def test_domain_not_zero_passes(test_domain_not_zero_passes_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_domain_not_zero_passes_df)

    rules = [
        {
            "dataframe_ids": [df_id],
            "type": "test_domains_not_zero",
            "column": "Value"
        }
    ]
    df_store = {df_id: test_domain_not_zero_passes_df}
    report = run_rules(df_store, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 1, json.dumps(report, indent=4)
    assert report["failed"] == 0, json.dumps(report, indent=4)

def test_domain_not_zero_fails_1(test_domain_not_zero_fails_1_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_domain_not_zero_fails_1_df)

    rules = [
        {
            "dataframe_ids": [df_id],
            "type": "test_domains_not_zero",
            "column": "Value"
        }
    ]
    df_store = {df_id: test_domain_not_zero_fails_1_df}
    report = run_rules(df_store, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 0, json.dumps(report, indent=4)
    assert report["failed"] == 1, json.dumps(report, indent=4)

def test_domain_not_zero_fails_2(test_domain_not_zero_fails_2_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_domain_not_zero_fails_2_df)

    rules = [
        {
            "dataframe_ids": [df_id],
            "type": "test_domains_not_zero",
            "column": "Value"
        }
    ]
    df_store = {df_id: test_domain_not_zero_fails_2_df}
    report = run_rules(df_store, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 0, json.dumps(report, indent=4)
    assert report["failed"] == 1, json.dumps(report, indent=4)

# -------------------- TEST BOUNDARIES NOT ALL VALUES THE SAME --------------------
def test_boundaries_not_all_values_the_same_passes(test_boundaries_not_all_values_the_same_passes_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_boundaries_not_all_values_the_same_passes_df)

    rules = [
        {
            "dataframe_ids": [df_id],
            "type": "test_boundaries_not_all_values_the_same",
            "column": "Value"
        }
    ]
    df_store = {df_id: test_boundaries_not_all_values_the_same_passes_df}
    report = run_rules(df_store, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 1, json.dumps(report, indent=4)
    assert report["failed"] == 0, json.dumps(report, indent=4)

def test_boundaries_not_all_values_the_same_passes(test_boundaries_not_all_values_the_same_fails_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_boundaries_not_all_values_the_same_fails_df)

    rules = [
        {
            "dataframe_ids": [df_id],
            "type": "test_boundaries_not_all_values_the_same",
            "column": "Value"
        }
    ]
    df_store = {df_id: test_boundaries_not_all_values_the_same_fails_df}
    report = run_rules(df_store, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 0, json.dumps(report, indent=4)
    assert report["failed"] == 1, json.dumps(report, indent=4)

# -------------------- TEST BOUNDARIES SUM EQUALS --------------------
def test_boundaries_sum_equals_passes(test_boundaries_sum_equals_passes_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_boundaries_sum_equals_passes_df)

    rules = [
        {
            "dataframe_ids": [df_id],
            "type": "test_boundaries_sum_equals",
            "column": "Value",
            "value": 50
        }
    ]
    df_store = {df_id: test_boundaries_sum_equals_passes_df}
    report = run_rules(df_store, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 1, json.dumps(report, indent=4)
    assert report["failed"] == 0, json.dumps(report, indent=4)

def test_boundaries_sum_equals_fails_1(test_boundaries_sum_equals_fails_1_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_boundaries_sum_equals_fails_1_df)

    rules = [
        {
            "dataframe_ids": [df_id],
            "type": "test_boundaries_sum_equals",
            "column": "Value",
            "value": 50
        }
    ]
    df_store = {df_id: test_boundaries_sum_equals_fails_1_df}
    report = run_rules(df_store, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 0, json.dumps(report, indent=4)
    assert report["failed"] == 1, json.dumps(report, indent=4)

def test_boundaries_sum_equals_fails_2(test_boundaries_sum_equals_fails_2_df):
    df_id = f"dataframe_{str(uuid.uuid4())}"
    redis_store.save_dataframe(df_id, test_boundaries_sum_equals_fails_2_df)

    rules = [
        {
            "dataframe_ids": [df_id],
            "type": "test_boundaries_sum_equals",
            "column": "Value",
            "value": 100
        }
    ]
    df_store = {df_id: test_boundaries_sum_equals_fails_2_df}
    report = run_rules(df_store, rules)
    redis_store.delete_dataframe(df_id)

    assert report["passed"] == 0, json.dumps(report, indent=4)
    assert report["failed"] == 1, json.dumps(report, indent=4)
