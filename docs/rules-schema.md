# Meta-Schema Specification for YAML Rules

This describes all supported rule types.

## 🔤 Primitive Types

### string

-   required
-   min_length
-   max_length
-   regex

### int / float

-   required
-   min
-   max

### bool

-   required

## 📁 Filesystem Types

### file

-   required
-   extensions

### directory

-   required
-   absolute

## 🔢 Enum

    mode:
      type: enum
      allowed: ["fast", "slow"]

## 📚 List

    samples:
      type: list
      element_type: string
      min_length: 1

## Extra Keys

`--allow-extra-keys` or `--no-allow-extra-keys`
