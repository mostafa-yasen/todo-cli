# Contributing Guidelines

Thank you for considering contributing to this project!

## Development Setup

1. **Clone and install:**
   ```bash
   git clone https://github.com/mostafa-yasen/todo-cli.git
   cd todo-cli
   uv sync --dev
   ```

2. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

## Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feat/your-feature
   ```

2. **Make your changes and ensure quality:**
   ```bash
   # Run tests
   pytest

   # Run type checking
   mypy src/

   # Run linting
   ruff check src/ tests/
   ```

3. **Commit with conventional commit format:**
   ```
   feat: add new feature
   fix: resolve bug
   docs: update documentation
   test: add tests
   refactor: code improvements
   ```

4. **Push and create PR:**
   - All CI checks must pass
   - Maintain 80%+ code coverage
   - Add tests for new features
   - Update documentation as needed

## Code Standards

- **Type hints**: Required for all functions
- **Tests**: Required for new features (80% coverage minimum)
- **Documentation**: Update README for user-facing changes
- **Style**: Follow Ruff formatting (runs automatically via pre-commit)

## Questions?

Open an issue for discussion before starting major changes.
