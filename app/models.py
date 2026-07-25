from typing import Literal

from pydantic import BaseModel, Field


class ValidationSummary(BaseModel):
    passed_rules: int = 0
    failed_rules: int = 0
    passed_checks: int = 0
    failed_checks: int = 0


class ValidationIssue(BaseModel):
    specification: str = ""
    clause: str = ""
    test_number: str = ""
    description: str = ""
    object: str = ""
    occurrences: int = 0
    contexts: list[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    status: Literal["compliant", "non_compliant"]
    profile: str
    duration_ms: int
    summary: ValidationSummary
    issues: list[ValidationIssue] = Field(default_factory=list)
