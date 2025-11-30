from pathlib import Path

import yaml

from jps_yaml_schema_validator.validator import validate_config_against_schema


def test_file_rule_missing_required(tmp_path: Path) -> None:
    schema = {
        "reference_genome": {
            "type": "file",
            "required": True,
            "must_exist": True,
        }
    }
    config = {}

    issues = validate_config_against_schema(schema=schema, config=config)
    assert len(issues) == 1
    assert "Missing required field" in str(issues[0])


def test_file_rule_exists(tmp_path: Path) -> None:
    fasta = tmp_path / "hg38.fa"
    fasta.write_text(">chr1\nACGT\n", encoding="utf-8")

    schema = {
        "reference_genome": {
            "type": "file",
            "required": True,
            "must_exist": True,
            "must_be_readable": True,
            "non_empty": True,
            "extensions": [".fa", ".fasta"],
        }
    }
    config = {"reference_genome": str(fasta)}

    issues = validate_config_against_schema(schema=schema, config=config)
    assert issues == []
