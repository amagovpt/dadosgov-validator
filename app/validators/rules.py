"""
Sample Validation Rules
=======================
These are placeholder implementations to get you started.
Replace or extend these with your existing validation logic.

Each function receives:
  - list of DataFrames (containing one or more datasets, covering rules that compare one or multiple datasets)
  - rule: the rule dict from the request

Each function returns:
  - A list of failure dicts (empty list = all rows passed)

Failure dict shape (customise as needed):
  {"row": <int>, "column": <str>, "value": <any>, "message": <str>}
"""

import pandas as pd


# --- Helpers ---

def _require_column(df: pd.DataFrame, rule: dict) -> str:
    """Extracts and validates the 'column' key from a rule dict."""
    column = rule.get("column")
    if not column:
        raise ValueError(f"Rule '{rule.get('type')}' requires a 'column' key")
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in dataset. Available columns: {list(df.columns)}")
    return column

# --- Rule implementations ---

def test_not_null(df_list: list, rule: dict) -> list:
    """Fails for any row where the column value is null/NaN."""
    assert len(df_list) == 1, "test_not_null expects exactly one dataset"
    df = df_list[0]  # Assuming we're working with the first DataFrame
    
    column = _require_column(df, rule)
    failures = []
    for idx, value in df[column].items():
        if pd.isna(value):
            failures.append({"row": int(idx), "column": column, "value": None, "message": "O valor é nulo/vazio"})

    return failures

def test_unique_generic(df_list: list, rule: dict) -> list:
    """Fails for any column or combination of columns that has duplicate values."""
    assert len(df_list) == 1, "test_unique_generic expects exactly one dataset"
    df = df_list[0]

    columns = rule.get("columns")
    if not isinstance(columns, list):
        raise ValueError("Rule 'unique_generic' requires a 'columns' key with a list")
    duplicates = df[df[columns].duplicated(keep=False)]
    failures = []
    for idx, row in duplicates.iterrows():
        failures.append({
            "row": int(idx), "column": ", ".join(columns), "value": row[columns].to_dict(),
            "message": f"Valor(es) duplicados na(s) coluna(s): {columns}"
        })

    return failures

def test_length_max(df_list: list, rule: dict) -> list:
    """
    Fails for rows where the length of the string in the column exceeds max_length. 
    Casts to text and ignores '.' when counting length on numeric values. Ignores null/NaN values.
    """
    assert len(df_list) == 1, "test_length_max expects exactly one dataset"
    df = df_list[0]
    
    column = _require_column(df, rule)
    max_length = rule.get("max_length")

    if max_length is None:
        raise ValueError("Rule 'test_length_max' requires a 'max_length' key with an integer value")
    
    try:
        max_length = int(max_length)
    except ValueError:
        raise ValueError("Rule 'test_length_max' requires 'max_length' to be an integer")

    failures = []
    for idx, value in df[column].items():
        if pd.isna(value):
            continue
        try:
            try:
                float(value)

                str_value = str(value)
                if '.' in str_value:
                    left_value, right_value = str_value.split('.', 1)
                    try:
                        if int(right_value) == 0:
                            text_value = left_value
                        else:
                            text_value = left_value + right_value

                    except ValueError:
                        # If right part is not numeric, treat the whole string as text
                        text_value = str_value

            except ValueError:
                # If value cannot be cast to float, treat it as text
                text_value = str(value)

            if len(text_value) > max_length:
                failures.append({"row": int(idx), "column": column, "value": value, "message": f"O valor excede o comprimento máximo de {max_length}"})
        except Exception as e:
            failures.append({"row": int(idx), "column": column, "value": value, "message": f"Erro ao processar o valor: {e}"})

    return failures

def test_length_min(df_list: list, rule: dict) -> list:
    """
    Fails for rows where the length of the string in the column is less than min_length. 
    Casts to text and ignores '.' when counting length on numeric values. Ignores null/NaN values.
    """
    assert len(df_list) == 1, "test_length_min expects exactly one dataset"
    df = df_list[0]

    column = _require_column(df, rule)
    min_length = rule.get("min_length")

    if min_length is None:
        raise ValueError("Rule 'test_length_min' requires a 'min_length' key with an integer value")
    
    try:
        min_length = int(min_length)
    except ValueError:
        raise ValueError("Rule 'test_length_min' requires 'min_length' to be an integer")

    failures = []
    for idx, value in df[column].items():
        if pd.isna(value):
            continue
        try:
            try:
                float(value)

                str_value = str(value)
                if '.' in str_value:
                    left_value, right_value = str_value.split('.', 1)
                    try:
                        if int(right_value) == 0:
                            text_value = left_value
                        else:
                            text_value = left_value + right_value

                    except ValueError:
                        # If right part is not numeric, treat the whole string as text
                        text_value = str_value

            except ValueError:
                # If value cannot be cast to float, treat it as text
                text_value = str(value)

            if len(text_value) < min_length:
                failures.append({"row": int(idx), "column": column, "value": value, "message": f"O valor é menor que o comprimento mínimo de {min_length}"})
        except Exception as e:
            failures.append({"row": int(idx), "column": column, "value": value, "message": f"Erro ao processar o valor: {e}"})

    return failures

def test_length_exact(df_list: list, rule: dict) -> list:
    """
    Fails for rows where the length of the string in the column is not equal to exact_length. 
    Casts to text and ignores '.' when counting length on numeric values. Ignores null/NaN values.
    """
    assert len(df_list) == 1, "test_length_exact expects exactly one dataset"
    df = df_list[0]

    column = _require_column(df, rule)
    exact_length = rule.get("exact_length")

    if exact_length is None:
        raise ValueError("Rule 'test_length_exact' requires a 'exact_length' key with an integer value")
    
    try:
        exact_length = int(exact_length)
    except ValueError:
        raise ValueError("Rule 'test_length_exact' requires 'exact_length' to be an integer")

    failures = []
    for idx, value in df[column].items():
        if pd.isna(value):
            continue
        try:
            try:
                float(value)

                str_value = str(value)
                if '.' in str_value:
                    left_value, right_value = str_value.split('.', 1)
                    try:
                        if int(right_value) == 0:
                            text_value = left_value
                        else:
                            text_value = left_value + right_value

                    except ValueError:
                        # If right part is not numeric, treat the whole string as text
                        text_value = str_value

            except ValueError:
                # If value cannot be cast to float, treat it as text
                text_value = str(value)

            if len(text_value) != exact_length:
                failures.append({"row": int(idx), "column": column, "value": value, "message": f"O valor não tem o comprimento exato de {exact_length}"})
        except Exception as e:
            failures.append({"row": int(idx), "column": column, "value": value, "message": f"Erro ao processar o valor: {e}"})

    return failures

def test_possible_values(df_list: list, rule: dict) -> list:
    """Fails if any of the non-null values in the column are not in the allowed set. Converts values to string for comparison, so that e.g. numeric 1 will match string "1" in the allowed set."""
    assert len(df_list) == 1, "test_possible_values expects exactly one dataset"
    df = df_list[0]

    column = _require_column(df, rule)
    allowed_values = set(rule.get("possible_values", []))
    if len(allowed_values) == 0:
        raise ValueError("Rule 'test_possible_values' requires a 'possible_values' key with a list of allowed values")
    failures = []
    for idx, value in df[column].items():
        if not pd.isna(value) and str(value) not in allowed_values:
            failures.append({"row": int(idx), "column": column, "value": value, "message": f"O valor não está no conjunto de valores permitidos"})
    return failures

def test_percentage_max_decimal_places(df: pd.DataFrame, rule: dict) -> list:
    """ For percentage (or decimal) columns: fails for rows where the number of decimal places exceeds max_number_decimal_places."""
    column = _require_column(df, rule)
    max_decimal_places = rule.get("max_decimal_places")

    if max_decimal_places is None:
        raise ValueError("Rule 'test_percentage_max_decimal_places' requires a 'max_decimal_places' key with an integer value")
    
    try:
        max_decimal_places = int(max_decimal_places)
    except ValueError:
        raise ValueError("Rule 'test_percentage_max_decimal_places' requires 'max_decimal_places' to be an integer")

    failures = []
    for idx, value in df[column].items():
        if pd.isna(value):
            continue
        try:
            decimal_part = str(value).split(".")[1] if "." in str(value) else ""
            if len(decimal_part) > max_decimal_places:
                failures.append({"row": int(idx), "column": column, "value": value, "message": f"O valor tem mais de {max_decimal_places} casas decimais"})
        except Exception as e:
            failures.append({"row": int(idx), "column": column, "value": value, "message": f"Erro ao processar o valor: {e}"})

    return failures

def test_domains_numeric(df_list: list, rule: dict) -> list:
    """
    Validates that a numeric column is within an allowed range.
        - If min_value is provided: fails rows where value < min_value
        - If max_value is provided: fails rows where value > max_value
        - If both are provided: fails rows outside [min_value, max_value]
    """
    assert len(df_list) == 1, "test_domains_numeric expects exactly one dataset"
    df = df_list[0]

    column = _require_column(df, rule)
    min_value = rule.get("min_value")
    max_value = rule.get("max_value")

    if min_value is None and max_value is None:
        raise ValueError("Rule 'test_domains_numeric' requires at least one of 'min_value' or 'max_value' to be provided")
    
    try:
        if min_value is not None:
            min_value = float(min_value)
        if max_value is not None:
            max_value = float(max_value)
    except ValueError:
        raise ValueError("Rule 'test_domains_numeric' requires 'min_value' and 'max_value' to be numeric if provided")

    failures = []
    for idx, value in df[column].items():
        if pd.isna(value):
            continue
        try:
            numeric_value = float(value)
            if (min_value is not None and numeric_value < min_value) or (max_value is not None and numeric_value > max_value):
                failures.append({"row": int(idx), "column": column, "value": value, "message": f"O valor está fora do intervalo permitido"})
        except Exception as e:
            failures.append({"row": int(idx), "column": column, "value": value, "message": f"Erro ao processar o valor: {e}"})

    return failures

def test_one_to_one_columns(df_list: list, rule: dict) -> list:
    """
    Validates that two columns have a one-to-one relationship (i.e. for each value in column1, 
    there is exactly one corresponding value in column2, and vice versa). Fails for any rows where 
    the combination of values in the specified columns is duplicated.
    """
    assert len(df_list) == 1, "test_one_to_one_columns expects exactly one dataset"
    df = df_list[0]

    column1 = rule.get("column1")
    column2 = rule.get("column2")

    if not column1 or not column2:
        raise ValueError("Rule 'test_one_to_one_columns' requires 'column1' and 'column2' keys")
    if column1 not in df.columns or column2 not in df.columns:
        raise ValueError(f"Columns '{column1}' and/or '{column2}' not found in dataset. Available columns: {list(df.columns)}")
    
    c1_groupby = df.groupby(column1)[column2].nunique()
    c2_groupby = df.groupby(column2)[column1].nunique()
    failures = []

    for value in c1_groupby[c1_groupby > 1].index:
        if pd.isna(value):
            continue
        failures.append({"column": column1, "value": value, "message": f"O valor em '{column1}' tem múltiplos valores correspondentes em '{column2}'"})

    for value in c2_groupby[c2_groupby > 1].index:
        if pd.isna(value):
            continue
        failures.append({"column": column2, "value": value, "message": f"O valor em '{column2}' tem múltiplos valores correspondentes em '{column1}'"})

    return failures

def test_boundaries_extended_table_coherence(df_list: list, rule: dict) -> list:
    assert len(df_list) == 2, "test_boundaries_extended_table_coherence expects exactly two datasets"
    df_source = df_list[0]
    df_extended = df_list[1]
    pass

