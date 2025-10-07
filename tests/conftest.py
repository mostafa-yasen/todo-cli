"""Test configuration and fixtures for the todo-cli test suite.

This module provides shared fixtures and configuration for testing,
demonstrating modern pytest practices.
"""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from click.testing import CliRunner

from todo_cli.models import TodoManager, TodoStorage


@pytest.fixture
def temp_storage_file() -> Generator[Path, None, None]:
    """Create a temporary storage file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def todo_storage(temp_storage_file: Path) -> TodoStorage:
    """Create a TodoStorage instance with temporary file."""
    return TodoStorage(temp_storage_file)


@pytest.fixture
def todo_manager(todo_storage: TodoStorage) -> TodoManager:
    """Create a TodoManager instance with temporary storage."""
    return TodoManager(todo_storage)


@pytest.fixture
def sample_todos(todo_manager: TodoManager) -> TodoManager:
    """Create a TodoManager with some sample todos for testing."""
    todo_manager.add_todo("Learn Python", "Study modern Python practices")
    todo_manager.add_todo("Write tests", "Create comprehensive test suite")
    todo_manager.add_todo("Deploy app", "Set up CI/CD pipeline")

    # Mark one as completed
    todos = todo_manager.get_todos()
    if todos:
        todo_manager.complete_todo(todos[0].id)

    return todo_manager


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def isolated_cli_runner(temp_storage_file: Path) -> tuple[CliRunner, Path]:
    """Create a CLI runner with isolated temporary storage."""
    runner = CliRunner()
    return runner, temp_storage_file
