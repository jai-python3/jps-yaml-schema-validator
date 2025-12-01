#!/usr/bin/env bash
# jps_yaml_schema_validator – tiny wrapper so users can run your tool like a native CLI
# Usage: jps_yaml_schema_validator validate schema.yaml data.yaml

set -euo pipefail

IMAGE="ghcr.io/jai-python3/jps-yaml-schema-validator:latest"
NAME="jps_yaml_schema_validator"

# Pull latest image quietly in the background (best-effort)
docker pull "$IMAGE" >/dev/null 2>&1 || true

# Run the container, mounting current directory as /data
exec docker run --rm -i \
  --volume "${PWD}:/data" \
  --workdir /data \
  "$IMAGE" "$@"