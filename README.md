# jps-yaml-schema-validator

![Build](https://github.com/jai-python3/jps-yaml-schema-validator/actions/workflows/test.yml/badge.svg)
![Publish to PyPI](https://github.com/jai-python3/jps-yaml-schema-validator/actions/workflows/publish-to-pypi.yml/badge.svg)
[![codecov](https://codecov.io/gh/jai-python3/jps-yaml-schema-validator/branch/main/graph/badge.svg)](https://codecov.io/gh/jai-python3/jps-yaml-schema-validator)

A strict, rule-driven YAML validator that verifies configuration files against a YAML-defined schema — supporting rich type checking, required fields, filesystem validation, enumerations, regex constraints, numeric ranges, list validation, and complete aggregated error reporting.

---

## 🚀 Overview

`jps-yaml-schema-validator` enables configuration-driven applications to validate user-supplied YAML files using a declarative rules file (also YAML).  

This library focuses on:

- **Strict validation** (no silently ignored fields)
- **Rich semantic checks**
- **Human-readable error messages**
- **Aggregated error reporting** (never fail fast)
- **CLI + Python API support**

Ideal for pipelines, workflow engines (Nextflow/Snakemake), microservices, CLIs, or any software that consumes YAML config files.

---

## ✨ Features

### **Supported rule types**
| Rule | Description |
|------|-------------|
| `required: true` | Field must exist |
| `type: string/int/float/bool` | Type enforcement |
| `type: file` | File must exist, readable, and not empty |
| `type: directory` | Must be an existing absolute directory |
| `allowed: [...]` | Enumerations |
| `regex: "pattern"` | Regex string validation |
| `min_length`, `max_length` | String length constraints |
| `min`, `max` | Numeric range checks |
| `element_type`, `min_items` | List validation |
| `allow_extra_keys` | Disable/enable acceptance of unknown keys |

### **Additional capabilities**

- Aggregates all validation errors before failing  
- Validates the schema file itself  
- Robust error messages  
- Clear CLI interface  
- 100% deterministic behavior  

---

## 📘 Example

### **rules.yaml**

```yaml
name:
  type: string
  required: true

threads:
  type: int
  required: true
  min: 1
  max: 64

input_file:
  type: file
  required: true

mode:
  type: string
  allowed:
    - fast
    - slow
```

### config.yaml
```yaml
name: "my job"
threads: 12
input_file: input.txt
mode: fast
```
### Validate using CLI

```bash
jps-yaml-schema-validate validate \
    --schema rules.yaml \
    --config config.yaml
```

### Output:

```bash
✅ Configuration is valid.
```

## ❌ Example validation failures


### If the user config violates rules:

```bash
❌ Validation failed:
  - Missing required key: name
  - Field 'threads' must be >= 1
  - Field 'input_file' must be an existing file
```


## 🧨 CLI Usage
```bash
jps-yaml-schema-validate validate --schema rules.yaml --config config.yaml
```


### Full help:

```bash
jps-yaml-schema-validate --help
```

## 🧵 Python API Usage
```python
from jps_yaml_schema_validator import assert_valid_config

schema = {
    "name": {"type": "string", "required": True},
    "threads": {"type": "int", "min": 1, "max": 16},
}

config = {"name": "job1", "threads": 8}

assert_valid_config(schema=schema, config=config)
```


## 📦 Installation

From source
```bash
make install
```

From PyPI

```bash
pip install jps-yaml-schema-validator
```

## 🧪 Development

```bash
make fix && make format && make lint
make test
```

### To run tests with coverage:

```bash
make test
```

## 📜 License
MIT License © Jaideep Sundaram