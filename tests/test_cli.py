import yaml
from pathlib import Path
from typer.testing import CliRunner

from jps_yaml_schema_validator.cli import app

runner = CliRunner()


def write_yaml(path: Path, data: dict) -> None:
    path.write_text(
        yaml.safe_dump(data, sort_keys=False),
        encoding="utf-8",
    )


def test_cli_valid(tmp_path: Path):
    """CLI should succeed with valid schema + config."""
    schema = {"name": {"type": "string", "required": True}}
    config = {"name": "hello"}

    s = tmp_path / "schema.yaml"
    c = tmp_path / "config.yaml"

    write_yaml(s, schema)
    write_yaml(c, config)

    result = runner.invoke(
        app,
        ["-s", str(s), "-c", str(c)],
        prog_name="jps-yaml-schema-validate",
    )

    assert result.exit_code == 0
    output = result.stdout.lower()
    assert "valid" in output


def test_cli_invalid(tmp_path: Path):
    """CLI should fail when validation issues occur."""
    schema = {"name": {"type": "string", "required": True}}
    config = {}

    s = tmp_path / "schema.yaml"
    c = tmp_path / "config.yaml"

    write_yaml(s, schema)
    write_yaml(c, config)

    result = runner.invoke(
        app,
        ["-s", str(s), "-c", str(c)],
        prog_name="jps-yaml-schema-validate",
    )

    assert result.exit_code == 1
    output = result.stdout.lower()
    assert "missing required" in output


def test_cli_disallow_extra_keys(tmp_path: Path):
    schema = {"name": {"type": "string", "required": True}}
    config = {"name": "hello", "unused": True}

    s = tmp_path / "schema.yaml"
    c = tmp_path / "config.yaml"

    write_yaml(s, schema)
    write_yaml(c, config)

    result = runner.invoke(
        app,
        ["-s", str(s), "-c", str(c), "--no-allow-extra-keys"],
        prog_name="jps-yaml-schema-validate",
    )

    assert result.exit_code == 1
    output = result.stdout.lower()
    assert "unexpected configuration key" in output


def test_cli_invalid_schema_yaml(tmp_path: Path):
    """Malformed schema YAML should produce exit code 2."""
    s = tmp_path / "schema.yaml"
    c = tmp_path / "config.yaml"

    s.write_text("::: bad YAML :::", encoding="utf-8")
    c.write_text("name: test", encoding="utf-8")

    result = runner.invoke(
        app,
        ["-s", str(s), "-c", str(c)],
        prog_name="jps-yaml-schema-validate",
    )

    assert result.exit_code == 2
    output = result.stdout.lower()
    assert "invalid yaml" in output


def test_cli_invalid_config_yaml(tmp_path: Path):
    """Malformed config YAML should produce exit code 2."""
    schema = {"name": {"type": "string", "required": True}}
    s = tmp_path / "schema.yaml"
    c = tmp_path / "config.yaml"

    write_yaml(s, schema)
    c.write_text(":: bad yaml ::", encoding="utf-8")

    result = runner.invoke(
        app,
        ["-s", str(s), "-c", str(c)],
        prog_name="jps-yaml-schema-validate",
    )

    assert result.exit_code == 2
    output = result.stdout.lower()
    assert "invalid yaml" in output
