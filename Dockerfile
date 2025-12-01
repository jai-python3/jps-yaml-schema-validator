# ============================
# Stage 1 — Build dependencies
# ============================
FROM python:3.12-slim AS builder

# Set workdir
WORKDIR /app

# Install build tools only for this stage
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy project metadata first (maximizes cache)
COPY pyproject.toml .
COPY src ./src

# Install project into a virtual environment
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip setuptools wheel && \
    /venv/bin/pip install .

# ============================
# Stage 2 — Runtime Image
# ============================
FROM python:3.12-slim AS runtime

# Do not run as root
RUN useradd -m appuser
USER appuser

# Set workdir
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /venv /venv

ENV PATH="/venv/bin:$PATH"

ENTRYPOINT ["jps-yaml-schema-validate"]
CMD ["--help"]
