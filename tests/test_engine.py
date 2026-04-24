"""
Basic tests for the validation engine.
Run with: pytest tests/
"""

import pandas as pd
import pytest
from app.validators.engine import run_rules


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "ID":     [1, 2, 2, 4],
        "Name":   ["Alice", "Bob", None, "Diana"],
        "Score":  [85, -5, 95, 110],
        "Status": ["active", "inactive", "active", "banned"],
    })


def test_not_null_passes(sample_df):
    rules = [{"type": "not_null", "column": "ID"}]
    report = run_rules(sample_df, rules)
    assert report["passed"] == 1
    assert report["failed"] == 0


def test_not_null_fails(sample_df):
    rules = [{"type": "not_null", "column": "Name"}]
    report = run_rules(sample_df, rules)
    assert report["failed"] == 1
    assert report["results"][0]["failures"][0]["row"] == 2


def test_min_value_fails(sample_df):
    rules = [{"type": "min_value", "column": "Score", "value": 0}]
    report = run_rules(sample_df, rules)
    assert report["failed"] == 1
    failures = report["results"][0]["failures"]
    assert len(failures) == 1
    assert failures[0]["value"] == -5


def test_max_value_fails(sample_df):
    rules = [{"type": "max_value", "column": "Score", "value": 100}]
    report = run_rules(sample_df, rules)
    assert report["failed"] == 1


def test_allowed_values_fails(sample_df):
    rules = [{"type": "allowed_values", "column": "Status", "values": ["active", "inactive"]}]
    report = run_rules(sample_df, rules)
    assert report["failed"] == 1
    assert report["results"][0]["failures"][0]["value"] == "banned"


def test_unique_fails(sample_df):
    rules = [{"type": "unique", "column": "ID"}]
    report = run_rules(sample_df, rules)
    assert report["failed"] == 1
    assert len(report["results"][0]["failures"]) == 2  # both duplicate rows


def test_unknown_rule_type(sample_df):
    rules = [{"type": "does_not_exist", "column": "ID"}]
    report = run_rules(sample_df, rules)
    assert report["failed"] == 1
    assert "Unknown rule type" in report["results"][0]["error"]


def test_multiple_rules(sample_df):
    rules = [
        {"type": "not_null",   "column": "ID"},
        {"type": "min_value",  "column": "Score", "value": 0},
        {"type": "unique",     "column": "ID"},
    ]
    report = run_rules(sample_df, rules)
    assert report["total_rules"] == 3
    assert report["passed"] == 1
    assert report["failed"] == 2
