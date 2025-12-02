# jps-yaml-schema-validator --- Usage Guide

This document explains how to use the CLI tool, including real-world
examples, exit codes, and Docker-based execution.

## 🚀 Basic Command

    jps-yaml-schema-validate --schema rules.yaml --config config.yaml

  Exit Code   Meaning
  ----------- -------------------------------------
  `0`         Configuration is valid
  `1`         Validation failed (schema mismatch)
  `2`         YAML parse error / unexpected error

## 📄 Example: Validate a Simple Config

### rules.yaml

``` yaml
name:
  type: string
  required: true
```

### config.yaml

``` yaml
name: "customer-service"
```

Run:

    jps-yaml-schema-validate -s rules.yaml -c config.yaml

Output:

    ✅ Configuration is valid.

## ❌ Example: Missing Required Field

config.yaml:

``` yaml
# name is missing
```

Run:

    jps-yaml-schema-validate -s rules.yaml -c config.yaml

Output:

    ❌ Validation failed:
      - Missing required field: name

## ⚠ Disallow Extra Keys

config.yaml:

``` yaml
name: hello
extra_field: true
```

Run:

    jps-yaml-schema-validate -s rules.yaml -c config.yaml --no-allow-extra-keys

Output:

    ❌ Validation failed:
      - Unexpected configuration key: extra_field


## 🐳 Native CLI via Docker wrapper (recommended)

Install a real shell command that runs the tool inside Docker (no Python required):

```bash
curl -sSL https://raw.githubusercontent.com/jai-python3/jps-yaml-schema-validator/main/jps_yaml_schema_validator.sh \
  | sudo tee /usr/local/bin/jps-yaml-schema-validate > /dev/null \
  && sudo chmod +x /usr/local/bin/jps-yaml-schema-validate
```

Now use it exactly like the PyPI-installed version:

```bash
jps-yaml-schema-validate validate --schema rules.yaml --config config.yaml
jps-yaml-schema-validate --help
```

The wrapper automatically pulls the latest image from GHCR.

Running via Docker (existing method – kept for reference)

Build:

```bash
docker build -t jps-yaml-schema-validator .
```

Run:
```bash
docker run --rm -v "$(pwd)":/data jps-yaml-schema-validator --schema /data/rules.yaml --config /data/config.yaml
```

Official pre-built image (no build required)

```bash
docker run --rm -v "$(pwd)":/data ghcr.io/jai-python3/jps-yaml-schema-validator:latest \
    validate --schema /data/rules.yaml --config /data/config.yaml
```

All three methods are supported indefinitely.