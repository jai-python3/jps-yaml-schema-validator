SHELL := /bin/bash

PACKAGE_NAME := jps-yaml-schema-validator
PYTHON := python3
PIP := pip
CURRENT_VERSION := $(shell grep -m1 '^version =' pyproject.toml | sed 's/.*"\(.*\)".*/\1/')
DRYRUN ?= 0


.PHONY: build \
check-build \
clean \
creat-venv \
fix \
format \
help \
install \
install-build-tools \
install-dev-tools \
lint \
precommit \
publish \
test \
uninstall \
version \
vulture 

# -----------------------------------------------------------
# Help
# -----------------------------------------------------------
help:
	@echo ""
	@echo "Available make targets:"
	@echo "  make build                 - Build source and wheel distributions"
	@echo "  make check-build           - Check built distributions"
	@echo "  make clean                 - Remove build artifacts and caches"
	@echo "  make create-venv           - Create a virtual environment"
	@echo "  make fix                   - Auto-fix code issues"
	@echo "  make format                - Format code with black"
	@echo "  make help                  - Show this help message"
	@echo "  make install               - Install package locally (editable mode)"
	@echo "  make install-build-tools   - Install build tools"
	@echo "  make install-dev-tools     - Install build dependencies"
	@echo "  make lint                  - Run flake8 lint checks"
	@echo "  make precommit             - Run pre-commit hooks on all files"
	@echo "  make publish               - Publish package to PyPI"
	@echo "  make test                  - Run tests with pytest"
	@echo "  make uninstall             - Uninstall package"
	@echo "  make version               - Show current version"
	@echo "  make vulture               - Run Vulture dead code analysis"

# -----------------------------------------------------------
# Create Virtual Environment
# -----------------------------------------------------------
create-venv:
	@echo ""
	@echo "🐍 Creating virtual environment 'venv'..."
	$(PYTHON) -m venv .venv
	source .venv/bin/activate && pip install --upgrade pip

# -----------------------------------------------------------
# Clean and Utility
# -----------------------------------------------------------
clean:
	@echo ""
	@echo "🧹 Cleaning build and cache artifacts..."
	rm -rf build dist .pytest_cache .coverage
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type d -name '*.egg-info' -exec rm -rf {} +

version:
	@echo ""
	@echo "📦 Current version: $(CURRENT_VERSION)"

# -----------------------------------------------------------
# Install, Uninstall
# -----------------------------------------------------------
install-dev-tools:
	@echo ""
	@echo "🛠️  Installing dev dependencies..."
	$(PIP) install -e '.[dev]'

install:
	@echo ""
	@echo "📦 Installing package in editable mode..."
	$(PIP) install -e .

uninstall:
	@echo ""
	@echo "🗑️  Uninstalling package..."
	$(PIP) uninstall -y $(PACKAGE_NAME)

# -----------------------------------------------------------
# Build and Publish
# -----------------------------------------------------------

install-build-tools:
	@echo ""
	@echo "🛠️  Installing build tools..."
	$(PIP) install build twine


build: install-build-tools
	@echo ""
	@echo "🏗️  Building source and wheel distributions..."
	$(PYTHON) -m build --sdist --wheel --outdir dist/


check-build: install-build-tools
	@echo ""
	@echo "🔍 Checking built distributions..."
	twine check dist/*


publish: build check-build
	@echo ""
	@if [ "$(DRYRUN)" -eq "1" ]; then \
		echo "🚀 Publishing package to Test PyPI (dry run)..."; \
		twine upload --repository testpypi dist/*; \
	else \
		echo "🚀 Publishing package to PyPI..."; \
		twine upload dist/*; \
	fi

# -----------------------------------------------------------
# QA / Developer Convenience
# -----------------------------------------------------------
test:
	@echo ""
	@echo "🧪 Running pytest with coverage..."
	pytest -v --disable-warnings \
	  --cov=src/scripts \
	  --cov-report=term-missing \
	  --cov-report=xml \
	  --cov-config=.coveragerc \
	  --cov-branch \
	  --cov-fail-under=0 \
	  --cov-append \
	  --cov-context=test

lint: install-dev-tools
	@echo ""
	@echo "🔍 Running flake8 lint checks..."
	flake8 src tests

format: install-dev-tools
	@echo ""
	@echo "🎨 Formatting code with black..."
	black src tests

fix: install-dev-tools
	@echo ""
	@echo "🧹 Auto-removing unused imports, sorting, and formatting code..."
	autoflake --in-place --recursive --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports src tests
	isort src tests
	black src tests
	flake8 src tests

precommit: install-dev-tools
	@echo ""
	@echo "✅ Running pre-commit hooks on all files..."
	pre-commit run --all-files

vulture: install-dev-tools
	@echo ""
	@echo "🪶 Running Vulture dead code analysis..."
	vulture src --min-confidence 80 --exclude tests,venv,build,dist
