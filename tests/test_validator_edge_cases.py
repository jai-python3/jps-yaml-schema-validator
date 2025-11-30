import pytest
from pathlib import Path
from jps_yaml_schema_validator.validator import validate_config_against_schema


def test_unsupported_type():
    schema = {"x": {"type": "unknown"}}
    config = {"x": "value"}
    issues = validate_config_against_schema(schema, config)
    assert any("Unsupported type" in str(i) for i in issues)


def test_invalid_regex():
    schema = {"x": {"type": "string", "required": True, "regex": "["}}
    config = {"x": "hello"}
    issues = validate_config_against_schema(schema, config)
    assert any("Invalid regex" in str(i) for i in issues)


def test_file_value_wrong_type():
    schema = {"x": {"type": "file", "required": True}}
    config = {"x": 123}
    issues = validate_config_against_schema(schema, config)
    assert any("Expected file path string" in str(i) for i in issues)


def test_directory_wrong_type():
    schema = {"x": {"type": "directory", "required": True}}
    config = {"x": 123}
    issues = validate_config_against_schema(schema, config)
    assert any("Expected directory path string" in str(i) for i in issues)


def test_enum_allowed_not_list():
    schema = {"x": {"type": "enum", "allowed": "not a list"}}
    config = {"x": "anything"}
    issues = validate_config_against_schema(schema, config)
    assert any("Schema error" in str(i) for i in issues)


def test_directory_must_be_absolute(tmp_path):
    schema = {"x": {"type": "directory", "must_be_absolute": True, "must_exist": True}}
    d = tmp_path / "mydir"
    d.mkdir()
    config = {"x": str(d.relative_to(tmp_path))}
    issues = validate_config_against_schema(schema, config)
    assert any("must be absolute" in str(i).lower() for i in issues)


def test_list_element_type_unsupported():
    schema = {"x": {"type": "list", "element_type": "unknown"}}
    config = {"x": ["a"]}
    issues = validate_config_against_schema(schema, config)
    assert any("Unsupported type" in str(i) for i in issues)
