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
from dataclasses import dataclass


# --- Helpers ---

@dataclass
class FailureMessage:
    row: int = None
    column: str = None
    value: str = None
    message: str = None

    def to_dict(self):
        return {"row": self.row, "column": self.column, "value": self.value, "message": self.message}


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
            failures.append(FailureMessage(row=int(idx), column=column, value=None, message="O valor é nulo/vazio"))

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
        failures.append(FailureMessage(
            row=int(idx), column=", ".join(columns), value=row[columns].to_dict(),
            message=f"Valor(es) duplicados na(s) coluna(s): {columns}"
        ))

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
                failures.append(FailureMessage(row=int(idx), column=column, value=value, message=f"O valor excede o comprimento máximo de {max_length}"))
        except Exception as e:
            failures.append(FailureMessage(row=int(idx), column=column, value=value, message=f"Erro ao processar o valor: {e}"))

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
                failures.append(FailureMessage(row=int(idx), column=column, value=value, message=f"O valor é menor que o comprimento mínimo de {min_length}"))
        except Exception as e:
            failures.append(FailureMessage(row=int(idx), column=column, value=value, message=f"Erro ao processar o valor: {e}"))

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
                failures.append(FailureMessage(row=int(idx), column=column, value=value, message=f"O valor não tem o comprimento exato de {exact_length}"))
        except Exception as e:
            failures.append(FailureMessage(row=int(idx), column=column, value=value, message=f"Erro ao processar o valor: {e}"))

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
            failures.append(FailureMessage(row=int(idx), column=column, value=value, message=f"O valor não está no conjunto de valores permitidos"))
    return failures

def test_percentage_max_decimal_places(df_list: list, rule: dict) -> list:
    """ For percentage (or decimal) columns: fails for rows where the number of decimal places exceeds max_number_decimal_places."""
    assert len(df_list) == 1, "test_percentage_max_decimal_places expects exactly one dataset"
    df = df_list[0]

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
                failures.append(FailureMessage(row=int(idx), column=column, value=value, message=f"O valor tem mais de {max_decimal_places} casas decimais"))
        except Exception as e:
            failures.append(FailureMessage(row=int(idx), column=column, value=value, message=f"Erro ao processar o valor: {e}"))

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
                failures.append(FailureMessage(row=int(idx), column=column, value=value, message=f"O valor está fora do intervalo permitido"))
        except Exception as e:
            failures.append(FailureMessage(row=int(idx), column=column, value=value, message=f"Erro ao processar o valor: {e}"))

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
        failures.append(FailureMessage(column=column1, value=value, message=f"O valor em '{column1}' tem múltiplos valores correspondentes em '{column2}'"))

    for value in c2_groupby[c2_groupby > 1].index:
        if pd.isna(value):
            continue
        failures.append(FailureMessage(column=column2, value=value, message=f"O valor em '{column2}' tem múltiplos valores correspondentes em '{column1}'"))

    return failures

def test_boundaries_extended_table_coherence(df_list: list, rule: dict) -> list:
    """
    Checks if all values of a column in the base dataset are present in a specified column of an extended dataset. 
    Fails for any value in the base column that is not found in the extended column. Ignores null/NaN values.
    """
    assert len(df_list) == 2, "test_boundaries_extended_table_coherence expects exactly two datasets"
    df_base = df_list[0]
    df_extended = df_list[1]

    base_column = rule.get("base_column")
    extended_column = rule.get("extended_column")

    if not base_column or not extended_column:
        raise ValueError("Rule 'test_boundaries_extended_table_coherence' requires 'base_column' and 'extended_column' keys")
    if base_column not in df_base.columns:
        raise ValueError(f"Base column '{base_column}' not found in the first dataset. Available columns: {list(df_base.columns)}")
    if extended_column not in df_extended.columns:
        raise ValueError(f"Extended column '{extended_column}' not found in the second dataset. Available columns: {list(df_extended.columns)}")
    
    extended_values = set(df_extended[extended_column].dropna().astype(str))
    failures = []
    for value in set(df_base[base_column].dropna().astype(str)):
        if pd.isna(value):
            continue
        if str(value) not in extended_values:
            failures.append(FailureMessage(column=base_column, value=value, message=f"O valor em '{base_column}' não foi encontrado no campo correspondente em '{extended_column}'"))
    return failures

def test_domains_only_one_value_across_datasets(df_list: list, rule: dict) -> list:
    # test_domains_distinct_reference_dates_all at the airflow project
    """
    Validates that the first listed Dataframe contains one unique value for the specified column, and that
    all the other Dataframes contain only that value in the specified columns. Fails if the first Dataframe
    contains more than one unique value, or if any of the other Dataframes contain a value different from 
    the unique value in the first Dataframe. Ignores null/NaN values. 
    """
    assert len(df_list) >= 2, "test_domains_unique_value_across_datasets expects at least two datasets"
    df_base = df_list[0]
    base_column = rule.get("base_column")

    if not base_column:
        raise ValueError("Rule 'test_domains_unique_value_across_datasets' requires 'base_column' key")
    if base_column not in df_base.columns:
        raise ValueError(f"Reference column '{base_column}' not found in the first dataset. Available columns: {list(df_base.columns)}")
    
    unique_values = set(df_base[base_column].dropna().astype(str))
    if len(unique_values) != 1:
        raise ValueError(f"Column '{base_column}' in the first dataset must contain exactly one unique non-null value for this rule. Found values: {unique_values}")
    unique_value = unique_values.pop()

    extended_columns = rule.get("extended_columns")
    if not extended_columns:
        raise ValueError("Rule 'test_domains_unique_value_across_datasets' requires 'extended_columns' key")
    try:
        if len(extended_columns) < 1:
            raise ValueError("Parameter 'extended_columns' must containtain one or more itemns")
    except TypeError as e:
        raise ValueError(f"Parameter 'extended_columns' must be an array: {e}")

    failures = []
    for i, (df, column) in enumerate(zip(df_list[1:], extended_columns)):
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in dataset {i+2}. Available columns: {list(df.columns)}")
        
        for idx, value in df[column].items():
            if pd.isna(value):
                continue
            if str(value) != unique_value:
                failures.append(FailureMessage(row=int(idx), column=column, value=value, message=f"O valor deve ser '{unique_value}' para corresponder ao valor único encontrado em '{base_column}' no primeiro dataset"))
    
    return failures

def test_format_no_leading_whitespace(df_list: list, rule: dict):
    # test_domains_tabulation at the airflow project
    """
    Validates formatting issues in a text column. Fails for:
        - Values starting with an empty space
        - Values starting with a tab
    Ignores null/NaN values.
    """
    assert len(df_list) == 1, "test_format_no_leading_whitespace expects exactly one dataset"
    df = df_list[0]

    column = _require_column(df, rule)
    failures = []
    for idx, value in df[column].items():
        if pd.isna(value):
            continue

        if value.startswith(' '):
            failures.append(FailureMessage(row=int(idx), column=column, value=value, message="O valor começa com um espaço vazio"))
        elif value.startswith('\t'):
            failures.append(FailureMessage(row=int(idx), column=column, value=value, message="O valor começa com uma tabulação"))

    return failures

def test_domains_not_zero(df_list: list, rule: dict):
    """
    Fails for rows where the given column equals zero (string '0' or numeric 0).
    Ignores null/NaN values.
    """
    assert len(df_list) == 1, "test_domains_not_zero expects exactly one dataset"
    df = df_list[0]

    column = _require_column(df, rule)
    failures = []
    for idx, value in df[column].items():
        if pd.isna(value):
            continue

        try:
            if float(value) == 0:
                failures.append(FailureMessage(row=int(idx), column=column, value=value, message="O valor é igual a zero"))
        except ValueError:
            # Not a numeric value, thus not a failure
            pass

    return failures
        
def test_boundaries_not_all_values_the_same(df_list: list, rule: dict):
    """
    Fails if all the values in the given column are the same.
    Ignores null/NaN values.
    """
    assert len(df_list) == 1, "test_domains_not_zero expects exactly one dataset"
    df = df_list[0]

    column = _require_column(df, rule)
    unique_values = df[column].dropna().unique()
    if len(unique_values) == 0:
        return [FailureMessage(column=column, message=f"A coluna {column} não possui nenhum nenhum valor não nulo")]
    elif len(unique_values) == 1:
        return [FailureMessage(column=column, message=f"A coluna {column} possui somente um valor {unique_values[0]}")]

    return []
    
def test_boundaries_sum_equals(df_list: list, rule: dict):
    """
    Fails if the sum of the values in the specified column equals the specified value.
    Ignores null/NaN
    """
    assert len(df_list) == 1, "test_boundaries_sum_equals expects exactly one dataset"
    df = df_list[0]

    column = _require_column(df, rule)

    value_param_str = rule.get("value")
    if not value_param_str:
        raise ValueError("Rule test_boundaries_sum_equals requires a 'value' key")
    
    try:
        float(value_param_str)
    except ValueError:
        raise ValueError("The 'value' key must be numeric")
    
    calculated_total = 0
    value_error_found = False
    failures = []
    for idx, value in df[column].items():
        if pd.isna(value):
            continue

        try:
            calculated_total += float(value)
        except ValueError:
            failures.append(FailureMessage(row=int(idx), column=column, value=value, message=f"O valor não é numérico, e portanto não é possível ser utilizado para o cálculo de soma"))
            value_error_found = True

    if value_error_found:
        return failures
    else:
        rounded_total_param = round(float(value_param_str), 1)
        rounded_total_calculated = round(calculated_total, 1)
        if not rounded_total_param == rounded_total_calculated:
            return [FailureMessage(column=column, value=calculated_total, message=f"O valor total informado '{rounded_total_param}' não é igual ao valor total calculado '{rounded_total_calculated}'")]
        else:
            return []