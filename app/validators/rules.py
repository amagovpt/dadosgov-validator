"""
Sample Validation Rules
=======================
These are placeholder implementations to get you started.
Replace or extend these with your existing validation logic.

Each function receives:
  - df:   the full pandas DataFrame
  - rule: the rule dict from the request

Each function returns:
  - A list of failure dicts (empty list = all rows passed)

Failure dict shape (customise as needed):
  {"row": <int>, "column": <str>, "value": <any>, "message": <str>}
"""

import pandas as pd


def test_not_null(df: pd.DataFrame, rule: dict) -> list:
    """Fails for any row where the column value is null/NaN."""
    column = _require_column(df, rule)
    failures = []
    for idx, value in df[column].items():
        if pd.isna(value):
            failures.append({"row": int(idx), "column": column, "value": None, "message": "Value is null"})
    return failures

def test_unique_generic(df: pd.DataFrame, rule: dict) -> list:
    """Fails for any column or combination of columns that has duplicate values."""
    columns = rule.get("columns")
    if not isinstance(columns, list):
        raise ValueError("Rule 'unique_generic' requires a 'columns' key with a list")
    duplicates = df[df[columns].duplicated(keep=False)]
    failures = []
    for idx, row in duplicates.iterrows():
        failures.append({
            "row": int(idx), "column": ", ".join(columns), "value": row[columns].to_dict(),
            "message": f"Duplicate value(s) found in columns: {columns}"
        })
    return failures


def validate_min_value(df: pd.DataFrame, rule: dict) -> list:
    """Fails for any row where the column value is below the specified minimum."""
    column = _require_column(df, rule)
    minimum = rule.get("value")
    if minimum is None:
        raise ValueError("Rule 'min_value' requires a 'value' key")
    failures = []
    for idx, value in df[column].items():
        if pd.notna(value) and value < minimum:
            failures.append({
                "row": int(idx), "column": column, "value": value,
                "message": f"Value {value} is below minimum {minimum}"
            })
    return failures


def validate_max_value(df: pd.DataFrame, rule: dict) -> list:
    """Fails for any row where the column value exceeds the specified maximum."""
    column = _require_column(df, rule)
    maximum = rule.get("value")
    if maximum is None:
        raise ValueError("Rule 'max_value' requires a 'value' key")
    failures = []
    for idx, value in df[column].items():
        if pd.notna(value) and value > maximum:
            failures.append({
                "row": int(idx), "column": column, "value": value,
                "message": f"Value {value} exceeds maximum {maximum}"
            })
    return failures


def validate_allowed_values(df: pd.DataFrame, rule: dict) -> list:
    """Fails for any row where the column value is not in the allowed set."""
    column = _require_column(df, rule)
    allowed = rule.get("values")
    if not isinstance(allowed, list):
        raise ValueError("Rule 'allowed_values' requires a 'values' key with a list")
    failures = []
    for idx, value in df[column].items():
        if pd.notna(value) and value not in allowed:
            failures.append({
                "row": int(idx), "column": column, "value": value,
                "message": f"Value '{value}' is not in allowed values: {allowed}"
            })
    return failures


def validate_unique(df: pd.DataFrame, rule: dict) -> list:
    """Fails for any row where the column value is duplicated."""
    column = _require_column(df, rule)
    duplicates = df[df[column].duplicated(keep=False)]
    failures = []
    for idx, row in duplicates.iterrows():
        failures.append({
            "row": int(idx), "column": column, "value": row[column],
            "message": f"Duplicate value '{row[column]}' found"
        })
    return failures


# --- Helpers ---

def _require_column(df: pd.DataFrame, rule: dict) -> str:
    """Extracts and validates the 'column' key from a rule dict."""
    column = rule.get("column")
    if not column:
        raise ValueError(f"Rule '{rule.get('type')}' requires a 'column' key")
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in dataset. Available columns: {list(df.columns)}")
    return column
