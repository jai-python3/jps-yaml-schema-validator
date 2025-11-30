# Software Release SOP

## Purpose

This document defines the standard operating procedure (SOP) for releasing new versions of the **{{**CODE-REPOSITORY**}}**
package to GitHub and PyPI.
It ensures consistency, traceability, and quality control for all published releases.

---

## 1. Prerequisites

Before executing a release:

- All code modifications are complete and committed.
- All tests pass successfully:

```bash
  pytest -v
```

- The pull request (PR) has been reviewed, approved, and merged into the `develop` branch.
- The `develop` branch has been merged into `main`.
- You have a valid PyPI API token stored as a GitHub secret (`PYPI_API_TOKEN`).

---

## 2. Branching and Merge Workflow

1. **Feature or Bugfix Branch**
   - Develop code on a feature or bugfix branch:

   ```bash
     feature/JPS-XXXX-description
     bugfix/JPS-XXXX-description
   ```

   - Commit changes and push to remote.

2. **Merge to `develop`**
   - Create a pull request (PR) → target `develop`.
   - Ensure CI tests pass.
   - Obtain approval and merge.

3. **Merge to `main`**
   - Once tested and approved, merge `develop` → `main`.
   - The `main` branch represents the release-ready code.

---

## 3. Release Preparation

1. Checkout and update the `main` branch:

    ```bash
      git checkout main
      git pull origin main
    ```

2. Verify everything is clean:

    ```bash
      pytest -v
      git status
    ```

3. Ensure the version number you plan to release does not already exist on PyPI.

---

## 4. Release Execution

Execute the release process using the Makefile:

```markdown
<codeblock bash>
make release VERSION=x.y.z
</codeblock>
```

This command performs the following actions:

1. Updates the version number in `pyproject.toml`.
2. Commits the version bump (`Release vX.Y.Z`).
3. Creates and pushes a Git tag `vX.Y.Z`.
4. Builds the distribution artifacts (`sdist` and `wheel`).
5. Uploads to PyPI using `twine`.

---

## 5. Post-Release Automation (GitHub Actions)

When the tag `vX.Y.Z` is pushed to GitHub:

- The **Publish to PyPI** GitHub Actions workflow (`.github/workflows/publish-to-pypi.yml`) runs automatically.
- It rebuilds the package and uploads to PyPI securely using the `PYPI_API_TOKEN`.

Monitor workflow progress under:
**GitHub → Actions → Publish to PyPI**

---

## 6. Verification

After a successful workflow:

1. Confirm the release appears on PyPI:
   [https://pypi.org/project/{{**CODE-REPOSITORY**}}/](https://pypi.org/project/jps-yaml-schema-validator/)

2. Install and test the published package:

    ```bash
      pip install jps-yaml-schema-validator==x.y.z
      create-jira-workspace --help
    ```

3. Update internal documentation or Confluence pages to record the release version and date.

---

## 7. Optional Maintenance

- To clean local artifacts:

```bash
  make clean
```

- To build without releasing:

```bash
  make build
```

---

## 8. Summary of Workflow

| Step | Branch | Command | Description |
|------|---------|----------|-------------|
| 1 | feature/bugfix | `pytest -v` | Validate local work |
| 2 | feature/bugfix → develop | PR | Merge tested code |
| 3 | develop → main | PR | Promote stable build |
| 4 | main | `git pull origin main` | Sync local |
| 5 | main | `make release VERSION=x.y.z` | Tag, build, and publish |
| 6 | GitHub Actions | *automatic* | Uploads to PyPI |

---

## 9. Responsibilities

| Role | Responsibility |
|------|----------------|
| Developer | Implement, test, and validate code |
| Reviewer | Approve PRs to `develop` and `main` |
| Release Engineer | Execute `make release` and verify publish success |
| Maintainer | Update version history in `CHANGELOG.md` |

---

## 10. References

- [PyPI Publishing Guide](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- `Makefile` (included at project root)
- `docs/CHANGELOG.md`

---

## Document version: 1.0.0 — Maintained by {{**AUTHOR**}} <{{**AUTHOR-EMAIL**}}>
