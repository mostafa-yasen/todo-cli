# Todo CLI - Modern Python Project Blueprint

A comprehensive CLI-based todo application that serves as a blueprint for modern Python development practices. This project demonstrates industry standards and best practices that junior developers can learn from and adapt for company projects.

## 🎯 Learning Objectives

This project is designed to teach:

- **Modern Python Project Structure**: Using `src/` layout with proper packaging
- **Dependency Management**: Using `uv` and `pyproject.toml` for modern Python packaging
- **Type Hints**: Comprehensive type annotations throughout the codebase
- **Testing Practices**: Unit and integration testing with pytest
- **CLI Development**: Building robust command-line interfaces with Click and Rich
- **Code Quality**: Linting, formatting, and static analysis with modern tools
- **Documentation**: Writing clear, comprehensive documentation

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mostafa-yasen/todo-cli.git
   cd todo-cli
   ```

2. **Install dependencies using uv:**
   ```bash
   # Install the package and its dependencies
   uv sync

   # Or install in development mode with dev dependencies
   uv sync --dev
   ```

3. **Activate the virtual environment:**
   ```bash
   # On Windows
   .venv\Scripts\activate

   # On macOS/Linux
   source .venv/bin/activate
   ```

4. **Install the CLI tool:**
   ```bash
   uv pip install -e .
   ```

### Basic Usage

```bash
# Add a new todo
todo add "Learn Python" "Study modern Python practices"

# List all todos
todo list

# Complete a todo
todo complete 1

# List only pending todos
todo list --completed false

# Delete a todo (with confirmation)
todo delete 1

# Show statistics
todo stats

# Clear all completed todos
todo clear-completed

# Get help
todo --help
```

## 📁 Project Structure

```
todo-cli/
├── src/
│   └── todo_cli/           # Main package directory
│       ├── __init__.py     # Package initialization
│       ├── cli.py          # CLI interface with Click
│       └── models.py       # Data models and business logic
├── tests/                  # Test package
│   ├── __init__.py
│   ├── conftest.py         # Pytest fixtures and configuration
│   ├── test_models.py      # Unit tests for models
│   └── test_cli.py         # Integration tests for CLI
├── pyproject.toml          # Project configuration and dependencies
├── README.md               # This file
└── .gitignore             # Git ignore rules
```

### Why This Structure?

- **`src/` Layout**: Prevents accidental imports of uninstalled packages during development
- **`tests/` Directory**: Separate from source code, mirrors package structure
- **`pyproject.toml`**: Single configuration file for all Python tooling
- **Type Hints**: Throughout the codebase for better IDE support and documentation

## 🛠️ Development Workflow

### Setting Up Development Environment

1. **Install development dependencies:**
   ```bash
   uv sync --dev
   ```

2. **Install pre-commit hooks (recommended):**
   ```bash
   pre-commit install
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=todo_cli

# Run specific test file
pytest tests/test_models.py

# Run tests with verbose output
pytest -v

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

### Code Quality Tools

```bash
# Format code with ruff
ruff format

# Lint code with ruff
ruff check

# Fix auto-fixable linting issues
ruff check --fix

# Type checking with mypy
mypy src/

# Run all quality checks
ruff format && ruff check && mypy src/
```

### Building and Distribution

```bash
# Build the package
uv build

# Install in editable mode
uv pip install -e .

# Install from built wheel
uv pip install dist/todo_cli-*.whl
```

## 🧪 Testing Strategy

The project includes comprehensive tests demonstrating different testing patterns:

### Unit Tests (`test_models.py`)
- **Model Testing**: Data validation, serialization, business logic
- **Mocking**: External dependencies (file system, time)
- **Edge Cases**: Error conditions, boundary values
- **Fixtures**: Reusable test data and setup

### Integration Tests (`test_cli.py`)
- **CLI Testing**: Command-line interface using Click's test runner
- **End-to-End**: Complete user workflows
- **File Isolation**: Temporary files for testing storage
- **Error Scenarios**: Invalid inputs, missing files

### Test Configuration
- **pytest.ini**: Centralized test configuration in `pyproject.toml`
- **Coverage**: Minimum 80% coverage requirement
- **Markers**: Categorize tests as unit/integration/slow

## 📊 Modern Python Features Demonstrated

### 1. Type Hints and Annotations
```python
def add_todo(self, title: str, description: str = "") -> TodoItem:
    """Add a new todo item with full type safety."""
```

### 2. Dataclasses
```python
@dataclass
class TodoItem:
    title: str
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
```

### 3. Modern Error Handling
```python
try:
    with self.file_path.open("r", encoding="utf-8") as f:
        return json.load(f)
except (json.JSONDecodeError, OSError) as e:
    raise RuntimeError(f"Failed to load: {e}") from e
```

### 4. Pathlib for File Operations
```python
from pathlib import Path

def __init__(self, file_path: Path | str = "todos.json") -> None:
    self.file_path = Path(file_path)
```

### 5. Context Managers and Resource Management
```python
with self.file_path.open("w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
```

## ⚙️ Configuration Files Explained

### `pyproject.toml`
The single source of truth for project configuration:

- **Project Metadata**: Name, version, description, authors
- **Dependencies**: Runtime and development dependencies
- **Build System**: Modern build backend with hatchling
- **Tool Configuration**: pytest, mypy, ruff, coverage settings
- **Entry Points**: CLI command registration

### Key Sections:
```toml
[project]
# Project metadata and dependencies

[project.scripts]
todo = "todo_cli.cli:main"  # CLI entry point

[tool.pytest.ini_options]
# Test configuration

[tool.mypy]
# Type checking configuration

[tool.ruff]
# Linting and formatting configuration
```

## 🎨 CLI Design Philosophy

### User Experience
- **Clear Commands**: Intuitive verb-based commands (add, list, complete)
- **Rich Output**: Beautiful tables and colored status indicators
- **Help Text**: Comprehensive help for all commands and options
- **Confirmation**: Safety prompts for destructive operations
- **Feedback**: Clear success/error messages with actionable information

### Technical Implementation
- **Click Framework**: Industry-standard CLI framework with decorators
- **Rich Library**: Modern terminal formatting and colors
- **Error Handling**: Graceful error handling with user-friendly messages
- **Testing**: Comprehensive CLI testing with Click's test runner

## 🔧 Customization and Extension

### Adding New Commands

1. **Add command function in `cli.py`:**
```python
@cli.command()
@click.argument("priority", type=click.IntRange(1, 5))
@click.pass_context
def prioritize(ctx: click.Context, todo_id: int, priority: int) -> None:
    """Set todo priority (1-5)."""
    # Implementation here
```

2. **Extend the `TodoItem` model in `models.py`:**
```python
@dataclass
class TodoItem:
    priority: int = 3  # Add new field
    # ... existing fields
```

3. **Add corresponding tests:**
```python
def test_prioritize_todo(self, isolated_cli_runner):
    """Test setting todo priority."""
    # Test implementation
```

### Custom Storage Backends

Implement the storage interface for different backends:

```python
class DatabaseStorage(TodoStorage):
    """SQLite database storage implementation."""

    def load_todos(self) -> list[TodoItem]:
        # Database implementation
        pass

    def save_todos(self, todos: list[TodoItem]) -> None:
        # Database implementation
        pass
```

## 📚 Additional Resources

### Python Packaging
- [Python Packaging User Guide](https://packaging.python.org/)
- [PEP 621 - Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)

### Testing
- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Click Applications](https://click.palletsprojects.com/en/8.1.x/testing/)

### Code Quality
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Mypy Documentation](https://mypy.readthedocs.io/)

### CLI Development
- [Click Documentation](https://click.palletsprojects.com/)
- [Rich Documentation](https://rich.readthedocs.io/)

## 🤝 Contributing

This project serves as a learning resource. When contributing:

1. **Follow the established patterns** demonstrated in the codebase
2. **Add tests** for any new functionality
3. **Update documentation** to reflect changes
4. **Run quality checks** before submitting changes

### Development Checklist
- [ ] Code follows type hints and modern Python practices
- [ ] Tests added/updated with good coverage
- [ ] Documentation updated
- [ ] Code formatted with `ruff format`
- [ ] Linting passes with `ruff check`
- [ ] Type checking passes with `mypy`
- [ ] All tests pass with `pytest`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎓 Learning Path

For junior developers, we recommend studying the code in this order:

1. **`models.py`** - Data modeling, type hints, business logic
2. **`cli.py`** - CLI design, user interaction, integration
3. **`test_models.py`** - Unit testing patterns and practices
4. **`test_cli.py`** - Integration testing and CLI testing
5. **`pyproject.toml`** - Modern Python project configuration
6. **This README** - Documentation and development workflows

Each file includes extensive comments explaining the patterns and practices being demonstrated.

---

**Happy coding! 🐍✨**
