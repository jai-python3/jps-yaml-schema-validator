#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jps_yaml_schema_validator

YAML-driven schema validator for configuration files.

This package provides utilities to validate a user-specified YAML
configuration file against a YAML-based schema (rules file). The rules
file is declarative and supports:

* Required/optional fields.
* Primitive types (string, int, float, bool).
* Filesystem-aware types (file, directory).
* Enumerations and regex patterns.
* Numeric ranges and list element constraints.
* Aggregated error reporting without failing fast.
"""
__version__ = "0.0.0"
from __future__ import annotations

from .exceptions import SchemaValidationError, ValidationIssue
from .validator import (
    assert_valid_config,
    validate_config_against_schema,
)

__all__ = [
    "SchemaValidationError",
    "ValidationIssue",
    "validate_config_against_schema",
    "assert_valid_config",
]
