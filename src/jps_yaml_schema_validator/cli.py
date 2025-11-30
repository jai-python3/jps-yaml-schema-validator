#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cli.py

Command-line interface for jps_yaml_schema_validator.

Typical usage:

    jps-yaml-schema-validate --schema rules.yaml --config config.yaml
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
import yaml

from .exceptions import SchemaValidationError
from .validator import assert_valid_config

app = typer.Typer(add_completion=False, help="YAML schema-based configuration validator.")


@app.command()
def validate(
    schema: Path = typer.Option(
        ...,
        "--schema",
        "-s",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Path to YAML schema (rules) file.",
    ),
    config: Path = typer.Option(
        ...,
        "--config",
        "-c",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Path to YAML configuration file to validate.",
    ),
    allow_extra_keys: bool = typer.Option(
        True,
        "--allow-extra-keys/--no-allow-extra-keys",
        help="Allow configuration keys not defined in the schema.",
    )
) -> None:
    """Validate a configuration file against a schema."""
    try:
        with schema.open("r", encoding="utf-8") as fh:
            schema_data = yaml.safe_load(fh) or {}

        with config.open("r", encoding="utf-8") as fh:
            config_data = yaml.safe_load(fh) or {}

        assert_valid_config(
            schema=schema_data,
            config=config_data,
            allow_extra_keys=allow_extra_keys,
        )
    except SchemaValidationError as exc:
        typer.echo("❌ Validation failed:", err=True)
        for issue in exc.issues:
            typer.echo(f"  - {issue}", err=True)
        raise typer.Exit(code=1) from exc
    
    except yaml.YAMLError as exc:
        typer.echo(f"❌ Invalid YAML: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    
    except Exception as exc:  # pragma: no cover - defensive
        typer.echo(f"Unexpected error: {exc}", err=True)
        raise typer.Exit(code=2) from exc

    typer.echo("✅ Configuration is valid.")


def main() -> None:
    """Entry point for the CLI."""
    app()  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
