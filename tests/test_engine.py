"""
Basic tests for the validation engine.
Run with 'pytest' on the root folder.
"""

import pandas as pd
import pytest
from app.validators.engine import run_rules


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


# -------------------- TEST NOT NULL --------------------
def test_not_null_passes(test_not_null_df):
    rules = [{"type": "test_not_null", "column": "ID"}]
    report = run_rules(test_not_null_df, rules)
    
    assert report["passed"] == 1
    assert report["failed"] == 0

def test_not_null_fails(test_not_null_df):
    rules = [{"type": "test_not_null", "column": "Name"}]
    report = run_rules(test_not_null_df, rules)
    
    assert report["failed"] == 1
    assert report["results"][0]["failures"][0]["row"] == 2

# -------------------- TEST UNIQUE GENERIC --------------------
def test_unique_generic_passes_1(test_unique_generic_df):
    rules = [{"type": "test_unique_generic", "columns": ["a"]}]
    report = run_rules(test_unique_generic_df, rules)
    
    assert report["passed"] == 1
    assert report["failed"] == 0

def test_unique_generic_passes_2(test_unique_generic_df):
    rules = [{"type": "test_unique_generic", "columns": ["b", "c"]}]
    report = run_rules(test_unique_generic_df, rules)
    
    assert report["passed"] == 1
    assert report["failed"] == 0

def test_unique_generic_fails(test_unique_generic_df):
    rules = [{"type": "test_unique_generic", "columns": ["b"]}]
    report = run_rules(test_unique_generic_df, rules)
    
    assert report["failed"] == 1
    assert len(report["results"][0]["failures"]) == 4

# -------------------- TEST LENGTH MAX --------------------
def test_length_max_passes(test_generic_length_df):
    rules = [
        {"type": "test_length_max", "column": "Text", "max_length": 63},
        {"type": "test_length_max", "column": "Numbers", "max_length": 7}
    ]
    report = run_rules(test_generic_length_df, rules)
    print(report)

    assert report["passed"] == 2
    assert report["failed"] == 0

def test_length_max_fails(test_generic_length_df):
    rules = [
        {"type": "test_length_max", "column": "Text", "max_length": 13},
        {"type": "test_length_max", "column": "Numbers", "max_length": 5}
    ]
    report = run_rules(test_generic_length_df, rules)
    print(report)

    assert report["passed"] == 0
    assert report["failed"] == 2
    assert len(report["results"][0]["failures"]) == 2
    assert len(report["results"][1]["failures"]) == 2

# -------------------- TEST LENGTH MIN --------------------
def test_length_min_passes(test_generic_length_df):
    rules = [
        {"type": "test_length_min", "column": "Text", "min_length": 5},
        {"type": "test_length_min", "column": "Numbers", "min_length": 3}
    ]
    report = run_rules(test_generic_length_df, rules)
    print(report)

    assert report["passed"] == 2
    assert report["failed"] == 0

def test_length_min_fails(test_generic_length_df):
    rules = [
        {"type": "test_length_min", "column": "Text", "min_length": 10},
        {"type": "test_length_min", "column": "Numbers", "min_length": 6}
    ]
    report = run_rules(test_generic_length_df, rules)
    print(report)

    assert report["passed"] == 0
    assert report["failed"] == 2
    assert len(report["results"][0]["failures"]) == 1
    assert len(report["results"][1]["failures"]) == 3

# -------------------- TEST LENGTH EXACT --------------------
def test_length_exact_passes(test_length_exact_df):
    rules = [
        {"type": "test_length_exact", "column": "Text", "exact_length": 4},
        {"type": "test_length_exact", "column": "Numbers", "exact_length": 4}
    ]
    report = run_rules(test_length_exact_df, rules)
    print(report)

    assert report["passed"] == 2
    assert report["failed"] == 0

def test_length_exact_fails(test_length_exact_df):
    rules = [
        {"type": "test_length_exact", "column": "Text", "exact_length": 5},
        {"type": "test_length_exact", "column": "Numbers", "exact_length": 5}
    ]
    report = run_rules(test_length_exact_df, rules)
    print(report)

    assert report["passed"] == 0
    assert report["failed"] == 2
    assert len(report["results"][0]["failures"]) == 3
    assert len(report["results"][1]["failures"]) == 4

# -------------------- TEST POSSIBLE VALUES --------------------
def test_possible_values_passes(test_possible_values_df):
    rules = [{"type": "test_possible_values", "column": "Status", "possible_values": ["a", "b", "c", "d"]}]
    report = run_rules(test_possible_values_df, rules)

    assert report["passed"] == 1
    assert report["failed"] == 0

def test_possible_values_fails(test_possible_values_df):
    rules = [{"type": "test_possible_values", "column": "Status", "possible_values": ["a", "b"]}]
    report = run_rules(test_possible_values_df, rules)
    
    assert report["failed"] == 1
    assert len(report["results"][0]["failures"]) == 2

# -------------------- TEST PERCENTAGE MAX DECIMAL PLACES --------------------
def test_percentage_max_decimal_places_passes(test_percentage_max_decimal_places_df):
    rules = [{"type": "test_percentage_max_decimal_places", "column": "Percentage", "max_decimal_places": 5}]
    report = run_rules(test_percentage_max_decimal_places_df, rules)
    
    assert report["passed"] == 1
    assert report["failed"] == 0

def test_percentage_max_decimal_places_fails(test_percentage_max_decimal_places_df):
    rules = [{"type": "test_percentage_max_decimal_places", "column": "Percentage", "max_decimal_places": 3}]
    report = run_rules(test_percentage_max_decimal_places_df, rules)
    
    assert report["failed"] == 1
    assert len(report["results"][0]["failures"]) == 2

# -------------------- TEST DOMAINS NUMERIC --------------------
def test_domains_numeric_passes_1(test_domains_numeric_df):
    rules = [{"type": "test_domains_numeric", "column": "Value", "min_value": -10}]
    report = run_rules(test_domains_numeric_df, rules)
    
    assert report["passed"] == 1
    assert report["failed"] == 0

def test_domains_numeric_passes_2(test_domains_numeric_df):
    rules = [{"type": "test_domains_numeric", "column": "Value", "max_value": 200}]
    report = run_rules(test_domains_numeric_df, rules)
    
    assert report["passed"] == 1
    assert report["failed"] == 0

def test_domains_numeric_passes_3(test_domains_numeric_df):
    rules = [{"type": "test_domains_numeric", "column": "Value", "min_value": -10, "max_value": 200}]
    report = run_rules(test_domains_numeric_df, rules)
    
    assert report["passed"] == 1
    assert report["failed"] == 0

def test_domains_numeric_fails_1(test_domains_numeric_df):
    rules = [{"type": "test_domains_numeric", "column": "Value", "min_value": 0}]
    report = run_rules(test_domains_numeric_df, rules)

    assert report["failed"] == 1
    assert len(report["results"][0]["failures"]) == 1

def test_domains_numeric_fails_2(test_domains_numeric_df):
    rules = [{"type": "test_domains_numeric", "column": "Value", "max_value": 90}]
    report = run_rules(test_domains_numeric_df, rules)

    assert report["failed"] == 1
    assert len(report["results"][0]["failures"]) == 2

def test_domains_numeric_fails_3(test_domains_numeric_df):
    rules = [{"type": "test_domains_numeric", "column": "Value", "min_value": 0, "max_value": 90}]
    report = run_rules(test_domains_numeric_df, rules)

    assert report["failed"] == 1
    assert len(report["results"][0]["failures"]) == 3

# -------------------- TEST ONE TO ONE COLUMNS --------------------
def test_one_to_one_columns_passes(test_one_to_one_columns_passes_df):
    rules = [{"type": "test_one_to_one_columns", "column1": "Codigo", "column2": "Descricao"}]
    report = run_rules(test_one_to_one_columns_passes_df, rules)

    assert report["passed"] == 1
    assert report["failed"] == 0

def test_one_to_one_columns_fails(test_one_to_one_columns_fails_df):
    rules = [{"type": "test_one_to_one_columns", "column1": "Codigo", "column2": "Descricao"}]
    report = run_rules(test_one_to_one_columns_fails_df, rules)

    assert report["passed"] == 0
    assert report["failed"] == 1