"""Unit tests for Python ValidationResult evaluator."""

import pytest
from a2ui.core.validating.validation_result import (
    CheckRule,
    ValidationResult,
    normalize_validation_result,
)


def test_normalize_boolean_result():
    pass_res = normalize_validation_result(True, CheckRule(message="Required"))
    assert pass_res.valid is True
    assert pass_res.message is None

    fail_res = normalize_validation_result(
        False, CheckRule(message="Required", code="REQ")
    )
    assert fail_res.valid is False
    assert fail_res.message == "Required"
    assert fail_res.code == "REQ"


def test_normalize_dict_result():
    res = normalize_validation_result({
        "valid": False,
        "code": "INVALID_FORMAT",
        "message": "Invalid email address",
        "severity": "warning",
    })
    assert res.valid is False
    assert res.code == "INVALID_FORMAT"
    assert res.message == "Invalid email address"
    assert res.severity == "warning"


def test_normalize_validation_result_instance():
    v = ValidationResult(valid=False)
    res = normalize_validation_result(v, CheckRule(message="Instance fallback"))
    assert res.valid is False
    assert res.message == "Instance fallback"


def test_normalize_empty_string_message():
    res = normalize_validation_result(
        {"valid": False, "message": ""}, CheckRule(message="Should not overwrite")
    )
    assert res.valid is False
    assert res.message == ""
