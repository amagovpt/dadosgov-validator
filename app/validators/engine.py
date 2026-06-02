"""
Validation Engine
=================
This is the bridge between the Flask/Celery layer and the existing validation logic.

HOW TO INTEGRATE EXISTING VALIDATORS:
-------------------------------------------
Import the package directly:
    from validation_package import validate_not_null, validate_min_value

RULE FORMAT:
------------
Each rule is a dict with at minimum a "type" key.
Additional keys depend on the rule type. Examples:

    {"dataframe_ids": ["df1"], "type": "not_null",   "column": "Age"}
    {"dataframe_ids": ["df1"], "type": "min_value",  "column": "Score",  "value": 0}
"""

import pandas as pd
import time
from app.validators.rules import (
    test_not_null,
    test_unique_generic,
    test_length_max,
    test_length_min,
    test_length_exact,
    test_possible_values,
    test_percentage_max_decimal_places,
    test_domains_numeric,
    test_one_to_one_columns,
    test_boundaries_extended_table_coherence,
    test_domains_only_one_value_across_datasets,
    test_format_no_leading_whitespace
)

# Maps rule type strings to validator functions
# ADD YOUR OWN RULES HERE as you port them from the existing project
RULE_REGISTRY: dict = {
    'test_not_null': test_not_null,
    'test_unique_generic': test_unique_generic,
    'test_length_max': test_length_max,
    'test_length_min': test_length_min,
    'test_length_exact': test_length_exact,
    'test_possible_values': test_possible_values,
    'test_percentage_max_decimal_places': test_percentage_max_decimal_places,
    'test_domains_numeric': test_domains_numeric,
    'test_one_to_one_columns': test_one_to_one_columns,
    'test_boundaries_extended_table_coherence': test_boundaries_extended_table_coherence,
    'test_domains_only_one_value_across_datasets': test_domains_only_one_value_across_datasets,
    'test_format_no_leading_whitespace': test_format_no_leading_whitespace
}


def run_rules(df_store: dict[str, pd.DataFrame], rules: list) -> dict:
    """
    Runs all requested rules against the DataFrame and compiles a report.

    Returns a report dict:
    {
        "total_rules": 3,
        "passed": 2,
        "failed": 1,
        "results": [
            {"rule": {...}, "passed": True,  "failures": []},
            {"rule": {...}, "passed": False, "failures": [
                {"column": "NomeColuna", "message": "Lorem ipsum dolor sit", "row": 4, "value": -1},
                {"column": "NomeColuna", "message": "Lorem ipsum dolor sit", "row": 7, "value": -4},
                ...
            ]},
            ...
        ]
    }
    """
    start_time = time.time()
    results = []

    for rule in rules:
        rule_type = rule.get("type")
        if rule_type not in RULE_REGISTRY:
            raise ValueError(f"Unknown rule type: {rule_type}. Please add it to the RULE_REGISTRY.")
        validator_fn = RULE_REGISTRY[rule_type]
        
        rule_dataframe_ids = rule.get("dataframe_ids", [])
        if len(rule_dataframe_ids) == 0:
            raise ValueError(f"Rule of type {rule_type} is missing 'dataframe_ids' key or it is empty.")
        rule_df_list = [df_store[df_id] for df_id in rule_dataframe_ids]

        try:
            failures = validator_fn(rule_df_list, rule)
            results.append({
                "rule": rule,
                "passed": len(failures) == 0,
                "failures": failures
            })
        except Exception as e:
            results.append({
                "rule": rule,
                "passed": False,
                "error": str(e)
            })

    passed_count = sum(1 for r in results if r.get("passed"))
    end_time = time.time()

    return {
        "total_rules": len(rules),
        "passed": passed_count,
        "failed": len(rules) - passed_count,
        "results": results,
        "execution_time_seconds": round(end_time - start_time, 2)
    }
