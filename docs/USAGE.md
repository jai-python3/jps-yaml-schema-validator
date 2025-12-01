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

## 🐳 Running via Docker

Build:

    docker build -t jps-yaml-schema-validator .

Run:

    docker run --rm -v "$(pwd)":/data jps-yaml-schema-validator --schema /data/rules.yaml --config /data/config.yaml
