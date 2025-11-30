#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exceptions.py

Exception and error types for jps_yaml_schema_validator.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List, Optional


@dataclass
class ValidationIssue:
    """Represents a single validation issue.

    Attributes:
        field: Name of the configuration field associated with this issue.
        message: Human-readable description of the validation problem.
        rule: Optional rule dictionary that was applied when the
            validation issue occurred. This is primarily intended for
            debugging and advanced reporting.
    """

    field: str
    message: str
    rule: Optional[dict[str, Any]] = None

    def __str__(self) -> str:
        return f"{self.field}: {self.message}"


class SchemaValidationError(Exception):
    """Raised when configuration validation fails.

    This exception aggregates one or more :class:`ValidationIssue`
    instances. The string representation of the exception is a newline-
    joined list of formatted issues.

    Attributes:
        issues: List of validation issues that were detected.
    """

    def __init__(self, issues: Iterable[ValidationIssue]) -> None:
        self.issues: List[ValidationIssue] = list(issues)
        message = "\n".join(str(issue) for issue in self.issues)
        super().__init__(message)
