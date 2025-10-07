"""Modern Todo CLI - A blueprint for Python CLI applications.

This package demonstrates modern Python development practices including:
- Project structure with src/ layout
- Dependency management with uv and pyproject.toml
- Type hints and modern Python features
- Comprehensive testing with pytest
- CLI development with Click
"""

from todo_cli.cli import main
from todo_cli.models import TodoItem, TodoManager, TodoStorage

__version__ = "0.1.0"
__author__ = "Mostafa Yasin"
__email__ = "mostafa.a.yasin@gmail.com"

__all__ = ["main", "TodoItem", "TodoManager", "TodoStorage"]
