# CI/CD Workflows Documentation

## Overview

This project uses GitHub Actions for automated quality checks and releases.

## Workflows

### 1. CI Pipeline (`ci.yml`)

**Triggers:** Push to main/develop, Pull Requests, Manual dispatch

**Jobs:**
- **code-quality**: Runs pre-commit hooks, Ruff linting and formatting checks
- **type-checking**: Runs MyPy static type analysis
- **test**: Runs pytest across multiple OS (Ubuntu, Windows, macOS) with coverage reports
- **security**: Scans for vulnerabilities using Safety and Bandit
- **build**: Validates package builds and installation
- **dependency-review**: Reviews dependency changes (PR only)
- **ci-success**: Final gate ensuring all jobs pass

**Coverage:** Requires minimum 80% code coverage

### 2. PR Checks (`pr-checks.yml`)

**Triggers:** Pull Request events

**Jobs:**
- **pr-validation**: Validates PR title follows conventional commits
- **quick-checks**: Fast feedback on changed files only
- **coverage-diff**: Shows coverage impact with PR comments

## Running Checks Locally

Before pushing, run these commands:

```bash
# Install pre-commit hooks
pre-commit install

# Run all pre-commit checks
pre-commit run --all-files

# Run type checking
mypy src/

# Run tests with coverage
pytest --cov=todo_cli --cov-report=term-missing

# Run linting
ruff check src/ tests/

# Run formatting
ruff format src/ tests/
```

## Troubleshooting
**If CI fails:**
1. Check the specific job that failed in GitHub Actions
2. Run the same command locally to reproduce
3. Fix the issue and push again

**Common issues:**
- **Type errors**: Run `mypy src/` locally
- **Test failures**: Run `pytest -v` to see details
- **Coverage drop**: Add tests for new code
- **Linting errors**: Run `ruff check --fix` to auto-fix
