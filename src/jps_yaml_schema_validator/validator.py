#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validator.py

Core validation engine for jps_yaml_schema_validator.

The primary entrypoint is :func:`validate_config_against_schema`, which
accepts two Python mappings:

* schema: Parsed contents of a YAML schema (rules) file.
* config: Parsed contents of a user configuration YAML file.

The schema is expected to be a mapping from field name to a rule
dictionary. Example:

    reference_genome:
      type: file
      required: true
      must_exist: true
      must_be_readable: true
      non_empty: true
      extensions: [".fa", ".fasta"]

    depth_metric:
      type: enum
      required: true
      allowed: ["median", "trimmed_mean", "MAD"]

"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

from .exceptions import SchemaValidationError, ValidationIssue


@dataclass
class _Context:
    """Internal validation context.

    Attributes:
        allow_extra_keys: If False, keys present in the configuration
            but not defined in the schema will be reported as issues.
    """

    allow_extra_keys: bool = True


def validate_config_against_schema(
    schema: Mapping[str, Any],
    config: Mapping[str, Any],
    *,
    allow_extra_keys: bool = True,
) -> List[ValidationIssue]:
    """Validate a configuration mapping against a schema mapping.

    This function does not raise; it returns a list of
    :class:`ValidationIssue` instances. Use
    :func:`assert_valid_config` to raise if any issues are present.

    Args:
        schema: Mapping representing the validation schema (rules). The
            typical source is a YAML rules file.
        config: Mapping representing the user configuration to be
            validated. The typical source is a YAML configuration file.
        allow_extra_keys: If False, keys present in ``config`` but not
            in ``schema`` will be reported as issues.

    Returns:
        List of :class:`ValidationIssue` objects describing all detected
        validation problems.
    """
    issues: List[ValidationIssue] = []
    ctx = _Context(allow_extra_keys=allow_extra_keys)

    # 1. Validate each field defined in the schema.
    for field_name, rule in schema.items():
        # Skip reserved / meta keys (convention: leading underscores).
        if isinstance(field_name, str) and field_name.startswith("_"):
            continue

        _validate_field(
            field_name=field_name,
            rule=rule or {},
            config=config,
            ctx=ctx,
            issues=issues,
        )

    # 2. Optionally validate extra keys in config.
    if not ctx.allow_extra_keys:
        for field_name in config.keys():
            if field_name not in schema:
                issues.append(
                    ValidationIssue(
                        field=field_name,
                        message="Unexpected configuration key (not defined in schema).",
                        rule=None,
                    )
                )

    return issues


def assert_valid_config(
    schema: Mapping[str, Any],
    config: Mapping[str, Any],
    *,
    allow_extra_keys: bool = True,
) -> None:
    """Validate configuration and raise if any issues are found.

    Args:
        schema: Parsed schema (rules) mapping.
        config: Parsed configuration mapping.
        allow_extra_keys: Whether to allow keys in ``config`` that are
            not defined in the schema.

    Raises:
        SchemaValidationError: If any validation issues are detected.
    """
    issues = validate_config_against_schema(
        schema=schema,
        config=config,
        allow_extra_keys=allow_extra_keys,
    )
    if issues:
        raise SchemaValidationError(issues)


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #


def _validate_field(
    field_name: str,
    rule: Mapping[str, Any],
    config: Mapping[str, Any],
    ctx: _Context,
    issues: List[ValidationIssue],
) -> None:
    """Validate a single field according to its rule."""
    required = bool(rule.get("required", False))

    if field_name not in config:
        if required:
            issues.append(
                ValidationIssue(
                    field=field_name,
                    message="Missing required field.",
                    rule=dict(rule),
                )
            )
        # If not required and not present, nothing more to validate.
        return

    value = config.get(field_name)
    field_type = str(rule.get("type", "string"))

    if value is None:
        if required:
            issues.append(
                ValidationIssue(
                    field=field_name,
                    message="Required field is null.",
                    rule=dict(rule),
                )
            )
        return

    # Dispatch based on declared type.
    if field_type == "string":
        _validate_string(field_name, value, rule, issues)
    elif field_type == "int":
        _validate_int(field_name, value, rule, issues)
    elif field_type == "float":
        _validate_float(field_name, value, rule, issues)
    elif field_type == "bool":
        _validate_bool(field_name, value, rule, issues)
    elif field_type == "enum":
        _validate_enum(field_name, value, rule, issues)
    elif field_type == "file":
        _validate_file(field_name, value, rule, issues)
    elif field_type in {"dir", "directory"}:
        _validate_directory(field_name, value, rule, issues)
    elif field_type == "list":
        _validate_list(field_name, value, rule, issues)
    else:
        issues.append(
            ValidationIssue(
                field=field_name,
                message=f"Unsupported type in schema: {field_type!r}.",
                rule=dict(rule),
            )
        )


def _validate_string(
    field_name: str,
    value: Any,
    rule: Mapping[str, Any],
    issues: List[ValidationIssue],
) -> None:
    if not isinstance(value, str):
        issues.append(
            ValidationIssue(
                field=field_name,
                message=f"Expected string, got {type(value).__name__}.",
                rule=dict(rule),
            )
        )
        return

    min_length = rule.get("min_length")
    max_length = rule.get("max_length")
    pattern = rule.get("regex")

    if isinstance(min_length, int) and len(value) < min_length:
        issues.append(
            ValidationIssue(
                field=field_name,
                message=f"String shorter than minimum length {min_length}.",
                rule=dict(rule),
            )
        )

    if isinstance(max_length, int) and len(value) > max_length:
        issues.append(
            ValidationIssue(
                field=field_name,
                message=f"String longer than maximum length {max_length}.",
                rule=dict(rule),
            )
        )

    if pattern:
        try:
            regex = re.compile(str(pattern))
        except re.error as exc:
            issues.append(
                ValidationIssue(
                    field=field_name,
                    message=f"Invalid regex in schema: {exc}.",
                    rule=dict(rule),
                )
            )
            return

        if regex.fullmatch(value) is None:
            issues.append(
                ValidationIssue(
                    field=field_name,
                    message=f"Value does not match regex pattern {pattern!r}.",
                    rule=dict(rule),
                )
            )


def _validate_int(
    field_name: str,
    value: Any,
    rule: Mapping[str, Any],
    issues: List[ValidationIssue],
) -> None:
    if not isinstance(value, int):
        issues.append(
            ValidationIssue(
                field=field_name,
                message=f"Expected int, got {type(value).__name__}.",
                rule=dict(rule),
            )
        )
        return

    min_value = rule.get("min")
    max_value = rule.get("max")

    if min_value is not None and value < min_value:
        issues.append(
            ValidationIssue(
                field=field_name,
                message=f"Value {value} is less than minimum {min_value}.",
                rule=dict(rule),
            )
        )
    if max_value is not None and value > max_value:
        issues.append(
            ValidationIssue(
                field=field_name,
                message=f"Value {value} is greater than maximum {max_value}.",
                rule=dict(rule),
            )
        )


def _validate_float(
    field_name: str,
    value: Any,
    rule: Mapping[str, Any],
    issues: List[ValidationIssue],
) -> None:
    if not isinstance(value, (int, float)):
        issues.append(
            ValidationIssue(
                field=field_name,
                message=f"Expected float, got {type(value).__name__}.",
                rule=dict(rule),
            )
        )
        return

    numeric_value = float(value)
    min_value = rule.get("min")
    max_value = rule.get("max")

    if min_value is not None and numeric_value < float(min_value):
        issues.append(
            ValidationIssue(
                field=field_name,
                message=f"Value {numeric_value} is less than minimum {min_value}.",
                rule=dict(rule),
            )
        )
    if max_value is not None and numeric_value > float(max_value):
        issues.append(
            ValidationIssue(
                field=field_name,
                message=f"Value {numeric_value} is greater than maximum {max_value}.",
                rule=dict(rule),
            )
        )


def _validate_bool(
    field_name: str,
    value: Any,
    rule: Mapping[str, Any],
    issues: List[ValidationIssue],
) -> None:
    if not isinstance(value, bool):
        issues.append(
            ValidationIssue(
                field=field_name,
                message=f"Expected bool, got {type(value).__name__}.",
                rule=dict(rule),
            )
        )


def _validate_enum(
    field_name: str,
    value: Any,
    rule: Mapping[str, Any],
    issues: List[ValidationIssue],
) -> None:
    allowed = rule.get("allowed")
    if not isinstance(allowed, Iterable) or isinstance(allowed, (str, bytes)):
        issues.append(
            ValidationIssue(
                field=field_name,
                message="Schema error: 'allowed' must be a list/sequence for enum type.",
                rule=dict(rule),
            )
        )
        return

    allowed_values = list(allowed)
    if value not in allowed_values:
        issues.append(
            ValidationIssue(
                field=field_name,
                message=f"Value {value!r} not in allowed set {allowed_values!r}.",
                rule=dict(rule),
            )
        )


def _validate_file(
    field_name: str,
    value: Any,
    rule: Mapping[str, Any],
    issues: List[ValidationIssue],
) -> None:
    if not isinstance(value, str):
        issues.append(
            ValidationIssue(
                field=field_name,
                message=f"Expected file path string, got {type(value).__name__}.",
                rule=dict(rule),
            )
        )
        return

    path = Path(value)

    if rule.get("must_be_absolute", False) and not path.is_absolute():
        issues.append(
            ValidationIssue(
                field=field_name,
                message="File path must be absolute.",
                rule=dict(rule),
            )
        )

    if rule.get("must_exist", False) and not path.exists():
        issues.append(
            ValidationIssue(
                field=field_name,
                message=f"File does not exist: {value}.",
                rule=dict(rule),
            )
        )
        # If it does not exist, subsequent checks are not meaningful.
        return

    if rule.get("must_be_readable", False) and not os.access(path, os.R_OK):
        issues.append(
            ValidationIssue(
                field=field_name,
                message=f"File is not readable: {value}.",
                rule=dict(rule),
            )
        )

    if rule.get("non_empty", False) and path.exists():
        try:
            size = path.stat().st_size
        except OSError:
            issues.append(
                ValidationIssue(
                    field=field_name,
                    message=f"Unable to stat file: {value}.",
                    rule=dict(rule),
                )
            )
        else:
            if size == 0:
                issues.append(
                    ValidationIssue(
                        field=field_name,
                        message=f"File is empty: {value}.",
                        rule=dict(rule),
                    )
                )

    extensions = rule.get("extensions")
    if extensions:
        valid_exts = [str(ext) for ext in extensions]
        if not any(str(value).endswith(ext) for ext in valid_exts):
            issues.append(
                ValidationIssue(
                    field=field_name,
                    message=f"File extension not in allowed set {valid_exts!r}.",
                    rule=dict(rule),
                )
            )


def _validate_directory(
    field_name: str,
    value: Any,
    rule: Mapping[str, Any],
    issues: List[ValidationIssue],
) -> None:
    if not isinstance(value, str):
        issues.append(
            ValidationIssue(
                field=field_name,
                message=f"Expected directory path string, got {type(value).__name__}.",
                rule=dict(rule),
            )
        )
        return

    path = Path(value)

    if rule.get("must_be_absolute", False) and not path.is_absolute():
        issues.append(
            ValidationIssue(
                field=field_name,
                message="Directory path must be absolute.",
                rule=dict(rule),
            )
        )

    if rule.get("must_exist", False) and not path.is_dir():
        issues.append(
            ValidationIssue(
                field=field_name,
                message=f"Directory does not exist or is not a directory: {value}.",
                rule=dict(rule),
            )
        )


def _validate_list(
    field_name: str,
    value: Any,
    rule: Mapping[str, Any],
    issues: List[ValidationIssue],
) -> None:
    if not isinstance(value, list):
        issues.append(
            ValidationIssue(
                field=field_name,
                message=f"Expected list, got {type(value).__name__}.",
                rule=dict(rule),
            )
        )
        return

    min_items = rule.get("min_items")
    max_items = rule.get("max_items")

    if isinstance(min_items, int) and len(value) < min_items:
        issues.append(
            ValidationIssue(
                field=field_name,
                message=f"List has fewer than minimum {min_items} items.",
                rule=dict(rule),
            )
        )

    if isinstance(max_items, int) and len(value) > max_items:
        issues.append(
            ValidationIssue(
                field=field_name,
                message=f"List has more than maximum {max_items} items.",
                rule=dict(rule),
            )
        )

    element_type = rule.get("element_type")
    if not element_type:
        return

    # Reuse existing validators where possible.
    for idx, item in enumerate(value):
        element_field_name = f"{field_name}[{idx}]"
        element_rule: Dict[str, Any] = dict(rule)
        element_rule["type"] = element_type
        # List-level constraints do not apply per element.
        element_rule.pop("min_items", None)
        element_rule.pop("max_items", None)

        _validate_field(
            field_name=element_field_name,
            rule=element_rule,
            config={element_field_name: item},
            ctx=_Context(allow_extra_keys=True),
            issues=issues,
        )
