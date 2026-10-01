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

    {"dataframe_ids": ["df1"], "type": "test_not_null",   "column": "Age"}
    {"dataframe_ids": ["df1"], "type": "test_length_max",  "column": "Score",  "value": 10}
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
    test_format_no_leading_whitespace,
    test_domains_not_zero,
    test_boundaries_not_all_values_the_same,
    test_boundaries_sum_equals
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
    'test_format_no_leading_whitespace': test_format_no_leading_whitespace,
    'test_domains_not_zero': test_domains_not_zero,
    'test_boundaries_not_all_values_the_same': test_boundaries_not_all_values_the_same,
    'test_boundaries_sum_equals': test_boundaries_sum_equals
}


def run_rules(df_store: dict[str, pd.DataFrame], rules: list) -> dict:
    """
    Runs all requested rules against the DataFrame and compiles a report.

    Returns a report dict:
    {
        "total_rules": 3,
        "passed": 1,
        "failed": 2,
        "results": [
            {"rule": {...}, "passed": True,  "warning_only": False, "failures": []},
            {"rule": {...}, "passed": False, "warning_only": False, "failures": [
                {"column": "NomeColuna", "message": "Lorem ipsum dolor sit", "row": 4, "value": -1},
                {"column": "NomeColuna", "message": "Lorem ipsum dolor sit", "row": 7, "value": -4},
                ...
            ]},
            ...
        ],
        "internal_errors": [
            {"rule": {...}, "passed": False, "warning_only": False, "error": "..."}
        ],
        "execution_time_seconds": 0.12
    }

    "results" holds one entry per rule that ran to completion; "internal_errors"
    holds rules that raised. Rules in "internal_errors" are never counted as
    passed, so "failed" (total - passed) includes them.
    """
    start_time = time.time()
    rule_results = []
    internal_errors = []

    for rule in rules:
        rule_type = rule.get("type")
        if rule_type not in RULE_REGISTRY:
            raise ValueError(f"Unknown rule type: {rule_type}. Please add it to the RULE_REGISTRY.")
        validator_fn = RULE_REGISTRY[rule_type]
        
        rule_dataframe_ids = rule.get("dataframe_ids", [])
        if len(rule_dataframe_ids) == 0:
            raise ValueError(f"Rule of type {rule_type} is missing 'dataframe_ids' key or it is empty.")
        rule_df_list = [df_store[df_id] for df_id in rule_dataframe_ids]

        # if a rule is marked as "warning_only", it will not count as a failure in the overall report, but will still be included in the results
        warning_only = rule.get("warning_only", False)

        try:
            failures = validator_fn(rule_df_list, rule)
            rule_results.append({
                "rule": rule,
                "passed": len(failures) == 0,
                "warning_only": warning_only,
                "failures": [f.to_dict() for f in failures]
            })
        except Exception as e:
            internal_errors.append({
                "rule": rule,
                "passed": False,
                "warning_only": warning_only,
                "error": str(e)
            })

    passed_count = sum(1 for r in rule_results if r.get("passed")) # does not include technical errors as those are always a failure
    end_time = time.time()

    return {
        "total_rules": len(rules),
        "passed": passed_count,
        "failed": len(rules) - passed_count,
        "results": rule_results,
        "internal_errors": internal_errors,
        "execution_time_seconds": round(end_time - start_time, 2)
    }
