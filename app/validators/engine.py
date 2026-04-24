"""
Validation Engine
=================
This is the bridge between the Flask/Celery layer and your existing validation logic.

HOW TO INTEGRATE YOUR EXISTING VALIDATORS:
-------------------------------------------
Import your package directly:
    from your_validation_package import validate_not_null, validate_min_value

RULE FORMAT:
------------
Each rule is a dict with at minimum a "type" key.
Additional keys depend on the rule type. Examples:

    {"type": "not_null",   "column": "Age"}
    {"type": "min_value",  "column": "Score",  "value": 0}
    {"type": "max_value",  "column": "Score",  "value": 100}
    {"type": "allowed_values", "column": "Status", "values": ["active", "inactive"]}
    {"type": "unique",     "column": "ID"}
"""

import pandas as pd
from app.validators.rules import (
    test_not_null
)

# Maps rule type strings to validator functions
# ADD YOUR OWN RULES HERE as you port them from your existing project
RULE_REGISTRY: dict = {
    'test_not_null': test_not_null,
}


def run_rules(df: pd.DataFrame, rules: list) -> dict:
    """
    Runs all requested rules against the DataFrame and compiles a report.

    Returns a report dict:
    {
        "total_rules": 3,
        "passed": 2,
        "failed": 1,
        "results": [
            {"rule": {...}, "passed": True,  "failures": []},
            {"rule": {...}, "passed": False, "failures": [{"row": 4, "value": -1}]},
            ...
        ]
    }
    """
    results = []

    for rule in rules:
        rule_type = rule.get("type")

        if rule_type not in RULE_REGISTRY:
            results.append({
                "rule": rule,
                "passed": False,
                "error": f"Unknown rule type: '{rule_type}'. Available types: {list(RULE_REGISTRY.keys())}"
            })
            continue

        validator_fn = RULE_REGISTRY[rule_type]

        try:
            failures = validator_fn(df, rule)
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

    return {
        "total_rules": len(rules),
        "passed": passed_count,
        "failed": len(rules) - passed_count,
        "results": results,
    }
