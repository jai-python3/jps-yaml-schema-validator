import os
from pathlib import Path
import yaml
import pytest

from jps_yaml_schema_validator.validator import (
    validate_config_against_schema,
    assert_valid_config,
)
from jps_yaml_schema_validator.exceptions import SchemaValidationError, ValidationIssue


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def write_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.dump(data), encoding="utf-8")


# ---------------------------------------------------------------------------
# Base schema used in most tests
# ---------------------------------------------------------------------------

@pytest.fixture
def schema():
    return {
        "ref": {
            "type": "file",
            "required": True,
            "must_exist": True,
            "must_be_readable": True,
            "non_empty": True,
            "extensions": [".fa"],
        },
        "outdir": {
            "type": "directory",
            "required": True,
            "must_exist": True,
        },
        "metric": {
            "type": "enum",
            "required": True,
            "allowed": ["a", "b", "c"],
        },
        "name": {
            "type": "string",
            "required": True,
            "min_length": 3,
            "max_length": 8,
            "regex": "^[A-Za-z]+$",
        },
        "count": {
            "type": "int",
            "required": True,
            "min": 1,
            "max": 5,
        },
        "threshold": {
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 1.0,
        },
        "flag": {
            "type": "bool",
            "required": True,
        },
        "genes": {
            "type": "list",
            "required": True,
            "min_items": 1,
            "max_items": 3,
            "element_type": "string",
        },
        "floats": {
            "type": "list",
            "required": True,
            "element_type": "float",
            "min_items": 2,
            "max_items": 4,
        },
    }


# ---------------------------------------------------------------------------
# Valid configuration
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_config(tmp_path: Path):
    fasta = tmp_path / "ref.fa"
    fasta.write_text(">chr1\nACGT\n", encoding="utf-8")

    outdir = tmp_path / "out"
    outdir.mkdir()

    return {
        "ref": str(fasta),
        "outdir": str(outdir),
        "metric": "a",
        "name": "Hello",
        "count": 3,
        "threshold": 0.5,
        "flag": True,
        "genes": ["A", "B"],
        "floats": [0.1, 0.9],
    }


# ---------------------------------------------------------------------------
# Basic: valid config should yield zero issues
# ---------------------------------------------------------------------------

def test_valid_config(schema, valid_config):
    issues = validate_config_against_schema(schema, valid_config)
    assert issues == []


# ---------------------------------------------------------------------------
# Missing required fields
# ---------------------------------------------------------------------------

def test_missing_required(schema, valid_config):
    del valid_config["metric"]
    issues = validate_config_against_schema(schema, valid_config)
    assert len(issues) == 1
    assert "Missing required field" in str(issues[0])


# ---------------------------------------------------------------------------
# File tests
# ---------------------------------------------------------------------------

def test_file_missing(schema, valid_config):
    valid_config["ref"] = "/path/does/not/exist.fa"
    issues = validate_config_against_schema(schema, valid_config)
    assert any("does not exist" in str(i) for i in issues)


def test_file_empty(schema, valid_config, tmp_path):
    empty = tmp_path / "empty.fa"
    empty.write_text("", encoding="utf-8")
    valid_config["ref"] = str(empty)
    issues = validate_config_against_schema(schema, valid_config)
    assert any("empty" in str(i) for i in issues)


def test_file_bad_extension(schema, valid_config, tmp_path):
    bad = tmp_path / "bad.txt"
    bad.write_text("content", encoding="utf-8")
    valid_config["ref"] = str(bad)
    issues = validate_config_against_schema(schema, valid_config)
    assert any("extension" in str(i) for i in issues)


# ---------------------------------------------------------------------------
# Directory tests
# ---------------------------------------------------------------------------

def test_directory_missing(schema, valid_config, tmp_path):
    valid_config["outdir"] = str(tmp_path / "does_not_exist")
    issues = validate_config_against_schema(schema, valid_config)
    assert any("does not exist" in str(i) for i in issues)


# ---------------------------------------------------------------------------
# Enum test
# ---------------------------------------------------------------------------

def test_enum_invalid(schema, valid_config):
    valid_config["metric"] = "X"
    issues = validate_config_against_schema(schema, valid_config)
    assert any("allowed" in str(i) for i in issues)


# ---------------------------------------------------------------------------
# String rules
# ---------------------------------------------------------------------------

def test_string_min_length(schema, valid_config):
    valid_config["name"] = "Hi"
    issues = validate_config_against_schema(schema, valid_config)
    assert any("minimum length" in str(i) for i in issues)


def test_string_max_length(schema, valid_config):
    valid_config["name"] = "TooLongName"
    issues = validate_config_against_schema(schema, valid_config)
    assert any("maximum length" in str(i) for i in issues)


def test_string_regex(schema, valid_config):
    valid_config["name"] = "123"
    issues = validate_config_against_schema(schema, valid_config)
    assert any("regex" in str(i) for i in issues)


# ---------------------------------------------------------------------------
# Int rules
# ---------------------------------------------------------------------------

def test_int_range(schema, valid_config):
    valid_config["count"] = 99
    issues = validate_config_against_schema(schema, valid_config)
    assert any("greater than maximum" in str(i) for i in issues)


# ---------------------------------------------------------------------------
# Float rules
# ---------------------------------------------------------------------------

def test_float_range(schema, valid_config):
    valid_config["threshold"] = -0.1
    issues = validate_config_against_schema(schema, valid_config)
    assert any("less than minimum" in str(i) for i in issues)


# ---------------------------------------------------------------------------
# Boolean rule
# ---------------------------------------------------------------------------

def test_bool_invalid(schema, valid_config):
    valid_config["flag"] = "yes"
    issues = validate_config_against_schema(schema, valid_config)
    assert any("Expected bool" in str(i) for i in issues)


# ---------------------------------------------------------------------------
# List item type validation
# ---------------------------------------------------------------------------

def test_list_element_type_invalid(schema, valid_config):
    valid_config["genes"] = ["A", 123]
    issues = validate_config_against_schema(schema, valid_config)
    assert any("genes[1]" in str(i) for i in issues)


def test_list_length_min(schema, valid_config):
    valid_config["genes"] = []
    issues = validate_config_against_schema(schema, valid_config)
    assert any("minimum" in str(i) for i in issues)


# ---------------------------------------------------------------------------
# Extra key detection
# ---------------------------------------------------------------------------

def test_extra_keys_disallowed(schema, valid_config):
    valid_config["extra"] = "value"
    issues = validate_config_against_schema(schema, valid_config, allow_extra_keys=False)
    assert any("Unexpected configuration key" in str(i) for i in issues)


# ---------------------------------------------------------------------------
# assert_valid_config error raising
# ---------------------------------------------------------------------------

def test_assert_valid_config_raises(schema, valid_config):
    valid_config["metric"] = "not_allowed"
    with pytest.raises(SchemaValidationError):
        assert_valid_config(schema, valid_config)
