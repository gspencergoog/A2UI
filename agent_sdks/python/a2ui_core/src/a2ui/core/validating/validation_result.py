"""Dynamic ValidationResult model and evaluator for A2UI v1.0 in Python."""

from typing import Optional, Literal, Union, Dict, Any
from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    """Dynamic validation result model."""

    valid: bool
    code: Optional[str] = None
    message: Optional[str] = None
    severity: Literal["error", "warning", "info"] = "error"


class CheckRule(BaseModel):
    """Check rule model providing message fallback."""

    message: Optional[str] = None
    code: Optional[str] = None


def normalize_validation_result(
    raw_result: Union[bool, Dict[str, Any], ValidationResult, None],
    rule: Optional[CheckRule] = None,
) -> ValidationResult:
    """Normalizes rule execution outputs into a canonical ValidationResult.

    Args:
        raw_result: Raw result (boolean or dictionary or ValidationResult object).
        rule: Fallback CheckRule definition providing static message or code.

    Returns:
        Canonical ValidationResult instance.
    """
    if isinstance(raw_result, ValidationResult):
        return raw_result

    if isinstance(raw_result, bool):
        return ValidationResult(
            valid=raw_result,
            code=rule.code if rule else None,
            message=None
            if raw_result
            else (rule.message if rule and rule.message else "Validation failed."),
            severity="error",
        )

    if isinstance(raw_result, dict):
        valid = bool(raw_result.get("valid", False))
        return ValidationResult(
            valid=valid,
            code=raw_result.get("code") or (rule.code if rule else None),
            message=raw_result.get("message")
            or (
                None
                if valid
                else (rule.message if rule and rule.message else "Validation failed.")
            ),
            severity=raw_result.get("severity", "error"),
        )

    return ValidationResult(
        valid=False,
        code=rule.code if rule else None,
        message=rule.message if rule and rule.message else "Validation failed.",
        severity="error",
    )
