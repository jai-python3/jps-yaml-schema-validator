# Developer SOP

## Purpose

This document describes the standardized development workflow for the **{{**CODE-REPOSITORY**}}** project.  
It ensures consistent local setup, testing, formatting, and release procedures aligned with the CI/CD pipelines.

---

## 1. Environment Setup

### 1.1 Prerequisites

- Python 3.11 or newer (Linux / WSL2 / macOS)
- Git
- Make
- Bash shell (required by Makefile)
- PyPI account and API token (for release maintainers)

### 1.2 Initial Setup

Clone the repository:

```bash
git clone git@github.com:jai-python3/jps-yaml-schema-validator.git
cd jps-yaml-schema-validator
```

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the package and development dependencies:

```bash
pip install -e '.[dev]'
```

Verify tools:

```bash
black --version
flake8 --version
pytest --version
release-management --version
```

---

## 2. Code Quality and Style

### 2.1 Linting and Formatting

Run **flake8** and **black** before committing:

```bash
make lint
make format
```

- `flake8` enforces PEP 8 and project-specific rules defined in `.flake8`.
- `black` automatically reformats code to a consistent 100-character width.

---

## 2. Testing

All tests are written using **pytest** and reside in the `tests/` directory.

Run the test suite:

```bash
make test
```

or directly:

```bash
pytest -v
```

CI automatically executes these tests on every push and pull request.

---

## 3. Versioning and Releases

### 4.1 Dry Run

Perform a dry run to simulate a release without committing or pushing changes:

```bash
make release PATCH DRYRUN=1
```

This confirms that version bumping and changelog generation work as expected.

### 4.2 Real Release

Perform a real semantic version bump and publish:

```bash
make release PATCH
# or
make release MINOR
# or
make release MAJOR
```

Actions performed automatically:

1. Bump version in `pyproject.toml`
2. Generate changelog with author + date
3. Commit and tag (`vX.Y.Z`)
4. Push changes and tags to GitHub
5. Build artifacts (`sdist` + `wheel`)
6. Upload to PyPI via Twine

### 4.3 Verification

After a release:

- Verify the GitHub Actions workflow **Publish to PyPI** completed successfully.
- Confirm the new version appears at [PyPI](https://pypi.org/project/jps-yaml-schema-validator/).
- Optionally test the installation:

```bash
pip install jps-yaml-schema-validator==<new_version>
```

---

## 5. Continuous Integration

Two GitHub Actions workflows are configured:

| Workflow | File | Trigger | Description |
|-----------|------|----------|--------------|
| Test | `.github/workflows/test.yml` | `push` and `pull_request` | Runs linting and pytest on all branches |
| Publish to PyPI | `.github/workflows/publish-to-pypi.yml` | `push` to tags `v*` | Builds and uploads package to PyPI |

Monitor workflows under **GitHub → Actions**.

---

## 6. Development Commands

| Command | Description |
|----------|--------------|
| `make help` | List all available Makefile commands |
| `make lint` | Run flake8 linting |
| `make format` | Auto-format code using black |
| `make test` | Run pytest suite |
| `make clean` | Remove build and cache artifacts |
| `make install-build-tools` | Install dev/test/build tools (`pip install -e '.[dev]'`) |
| `make version` | Display current version |

---

## 7. Troubleshooting

### 7.1 "Syntax error: redirection unexpected"

Add this line near the top of your Makefile:

```bash
SHELL := /bin/bash
```

### 7.2 "File already exists" during PyPI upload

Each PyPI release version is immutable.  
You must increment the version (e.g., `1.0.0` → `1.0.1`) before retrying.

### 7.3 Lint errors for line length 79 instead of 100

Ensure `.flake8` exists in the project root with:

```bash
max-line-length = 100
```

### 7.4 Removing release-management restrictions temporarily

```bash
git commit --no-verify
```

---

## 8. References

- PyPI Publishing Guide: <https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/>
- release-management Framework: <https://release-management.com/>
- Flake8 Rules: <https://flake8.pycqa.org/en/latest/user/error-codes.html>
- Black Formatter: <https://black.readthedocs.io/en/stable/>
- GitHub Actions Documentation: <https://docs.github.com/en/actions>

---

## Document version: 1.0.0 — Maintained by Jaideep Sundaram
