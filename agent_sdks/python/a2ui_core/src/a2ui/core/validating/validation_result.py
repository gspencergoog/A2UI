# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
    rule_code = rule.code if rule else None
    rule_msg = rule.message if rule else None

    if isinstance(raw_result, ValidationResult):
        msg = (
            raw_result.message
            if raw_result.message is not None
            else (
                None
                if raw_result.valid
                else (rule_msg if rule_msg is not None else "Validation failed.")
            )
        )
        code = raw_result.code if raw_result.code is not None else rule_code
        return ValidationResult(
            valid=raw_result.valid,
            code=code,
            message=msg,
            severity=raw_result.severity,
        )

    if isinstance(raw_result, bool):
        return ValidationResult(
            valid=raw_result,
            code=rule_code,
            message=None
            if raw_result
            else (rule_msg if rule_msg is not None else "Validation failed."),
            severity="error",
        )

    if isinstance(raw_result, dict):
        valid = bool(raw_result.get("valid", False))
        res_code = raw_result.get("code")
        code = res_code if res_code is not None else rule_code
        res_msg = raw_result.get("message")
        msg = (
            res_msg
            if res_msg is not None
            else (
                None
                if valid
                else (rule_msg if rule_msg is not None else "Validation failed.")
            )
        )
        raw_sev = raw_result.get("severity")
        severity: Literal["error", "warning", "info"] = (
            raw_sev if raw_sev in ("error", "warning", "info") else "error"
        )
        return ValidationResult(
            valid=valid,
            code=code,
            message=msg,
            severity=severity,
        )

    return ValidationResult(
        valid=False,
        code=rule_code,
        message=rule_msg if rule_msg is not None else "Validation failed.",
        severity="error",
    )
