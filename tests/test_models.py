"""Tests for the todo models module.

This module demonstrates comprehensive testing practices including:
- Unit testing with pytest
- Fixtures for test data
- Exception testing
- Edge case coverage
- Mocking external dependencies
"""

from __future__ import annotations

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from todo_cli.models import TodoItem, TodoManager, TodoStorage


class TestTodoItem:
    """Test cases for the TodoItem class."""

    def test_create_todo_item(self) -> None:
        """Test basic todo item creation."""
        todo = TodoItem("Learn Python", "Study modern practices")

        assert todo.title == "Learn Python"
        assert todo.description == "Study modern practices"
        assert not todo.completed
        assert todo.completed_at is None
        assert isinstance(todo.created_at, datetime)
        assert todo.id > 0

    def test_create_todo_item_minimal(self) -> None:
        """Test creating todo with minimal required fields."""
        todo = TodoItem("Buy milk")

        assert todo.title == "Buy milk"
        assert todo.description == ""
        assert not todo.completed
        assert todo.id > 0

    def test_empty_title_raises_error(self) -> None:
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="Todo title cannot be empty"):
            TodoItem("")

        with pytest.raises(ValueError, match="Todo title cannot be empty"):
            TodoItem("   ")  # Whitespace only

    def test_auto_increment_ids(self) -> None:
        """Test that IDs are auto-incremented."""
        todo1 = TodoItem("First")
        todo2 = TodoItem("Second")

        assert todo2.id > todo1.id

    def test_complete_todo(self) -> None:
        """Test completing a todo item."""
        todo = TodoItem("Test todo")
        assert not todo.completed
        assert todo.completed_at is None

        todo.complete()

        assert todo.completed
        assert todo.completed_at is not None
        assert isinstance(todo.completed_at, datetime)  # type: ignore[unreachable]

    def test_complete_already_completed_todo(self) -> None:
        """Test completing an already completed todo."""
        todo = TodoItem("Test todo")
        todo.complete()
        original_completed_at = todo.completed_at

        # Complete again
        todo.complete()

        # Should remain the same
        assert todo.completed
        assert todo.completed_at == original_completed_at

    def test_uncomplete_todo(self) -> None:
        """Test uncompleting a todo item."""
        todo = TodoItem("Test todo")
        todo.complete()

        todo.uncomplete()

        assert not todo.completed
        assert todo.completed_at is None

    def test_uncomplete_not_completed_todo(self) -> None:
        """Test uncompleting a todo that's not completed."""
        todo = TodoItem("Test todo")

        todo.uncomplete()

        # Should remain not completed
        assert not todo.completed
        assert todo.completed_at is None

    def test_to_dict(self) -> None:
        """Test converting todo to dictionary."""
        todo = TodoItem("Test todo", "Description")
        todo_dict = todo.to_dict()

        expected_keys = {
            "id",
            "title",
            "description",
            "completed",
            "created_at",
            "completed_at",
        }
        assert set(todo_dict.keys()) == expected_keys
        assert todo_dict["title"] == "Test todo"
        assert todo_dict["description"] == "Description"
        assert not todo_dict["completed"]
        assert todo_dict["completed_at"] is None

    def test_to_dict_completed(self) -> None:
        """Test converting completed todo to dictionary."""
        todo = TodoItem("Test todo")
        todo.complete()
        todo_dict = todo.to_dict()

        assert todo_dict["completed"]
        assert todo_dict["completed_at"] is not None

    def test_from_dict(self) -> None:
        """Test creating todo from dictionary."""
        data = {
            "id": 42,
            "title": "Test todo",
            "description": "Test description",
            "completed": False,
            "created_at": "2023-01-01T12:00:00",
            "completed_at": None,
        }

        todo = TodoItem.from_dict(data)

        assert todo.id == 42
        assert todo.title == "Test todo"
        assert todo.description == "Test description"
        assert not todo.completed
        assert todo.completed_at is None

    def test_from_dict_completed(self) -> None:
        """Test creating completed todo from dictionary."""
        data = {
            "id": 1,
            "title": "Test todo",
            "completed": True,
            "created_at": "2023-01-01T12:00:00",
            "completed_at": "2023-01-01T13:00:00",
        }

        todo = TodoItem.from_dict(data)

        assert todo.completed
        assert todo.completed_at is not None

    def test_roundtrip_serialization(self) -> None:
        """Test that serialization roundtrip preserves data."""
        original = TodoItem("Test todo", "Description")
        original.complete()

        # Serialize and deserialize
        data = original.to_dict()
        restored = TodoItem.from_dict(data)

        assert restored.id == original.id
        assert restored.title == original.title
        assert restored.description == original.description
        assert restored.completed == original.completed
        assert restored.created_at == original.created_at
        assert restored.completed_at == original.completed_at


class TestTodoStorage:
    """Test cases for the TodoStorage class."""

    def test_save_and_load_empty_list(self, temp_storage_file: Path) -> None:
        """Test saving and loading empty todo list."""
        storage = TodoStorage(temp_storage_file)

        storage.save_todos([])
        loaded_todos = storage.load_todos()

        assert loaded_todos == []

    def test_save_and_load_todos(self, temp_storage_file: Path) -> None:
        """Test saving and loading todo items."""
        storage = TodoStorage(temp_storage_file)

        todos = [
            TodoItem("First todo", "Description 1"),
            TodoItem("Second todo", "Description 2"),
        ]
        todos[0].complete()

        storage.save_todos(todos)
        loaded_todos = storage.load_todos()

        assert len(loaded_todos) == 2
        assert loaded_todos[0].title == "First todo"
        assert loaded_todos[0].completed
        assert loaded_todos[1].title == "Second todo"
        assert not loaded_todos[1].completed

    def test_load_nonexistent_file(self) -> None:
        """Test loading from nonexistent file returns empty list."""
        storage = TodoStorage("nonexistent.json")
        todos = storage.load_todos()

        assert todos == []

    def test_load_invalid_json(self, temp_storage_file: Path) -> None:
        """Test loading invalid JSON raises error."""
        temp_storage_file.write_text("invalid json content")
        storage = TodoStorage(temp_storage_file)

        with pytest.raises(RuntimeError, match="Failed to load todos"):
            storage.load_todos()

    def test_load_invalid_todo_data(self, temp_storage_file: Path) -> None:
        """Test loading invalid todo data raises error."""
        # Write invalid todo data
        invalid_data = [{"invalid": "data"}]
        temp_storage_file.write_text(json.dumps(invalid_data))

        storage = TodoStorage(temp_storage_file)

        with pytest.raises(RuntimeError, match="Failed to load todos"):
            storage.load_todos()

    @patch("pathlib.Path.open")
    def test_save_file_error(self, mock_open: Mock, temp_storage_file: Path) -> None:
        """Test handling file save errors."""
        mock_open.side_effect = OSError("Permission denied")
        storage = TodoStorage(temp_storage_file)

        with pytest.raises(RuntimeError, match="Failed to save todos"):
            storage.save_todos([])

    def test_create_parent_directories(self) -> None:
        """Test that parent directories are created when saving."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "nested" / "directory" / "todos.json"
            storage = TodoStorage(nested_path)

            # Parent directories shouldn't exist initially
            assert not nested_path.parent.exists()

            # Save should create them
            storage.save_todos([])

            assert nested_path.exists()
            assert nested_path.parent.exists()


class TestTodoManager:
    """Test cases for the TodoManager class."""

    def test_init_with_default_storage(self) -> None:
        """Test manager initialization with default storage."""
        manager = TodoManager()
        assert manager.storage is not None
        assert isinstance(manager.storage, TodoStorage)

    def test_init_with_custom_storage(self, todo_storage: TodoStorage) -> None:
        """Test manager initialization with custom storage."""
        manager = TodoManager(todo_storage)
        assert manager.storage is todo_storage

    def test_add_todo(self, todo_manager: TodoManager) -> None:
        """Test adding a todo item."""
        todo = todo_manager.add_todo("Test todo", "Description")

        assert todo.title == "Test todo"
        assert todo.description == "Description"
        assert not todo.completed

        # Should be in the manager's list
        todos = todo_manager.get_todos()
        assert todo in todos

    def test_get_todos_all(self, sample_todos: TodoManager) -> None:
        """Test getting all todos."""
        todos = sample_todos.get_todos()
        assert len(todos) == 3

    def test_get_todos_completed(self, sample_todos: TodoManager) -> None:
        """Test getting only completed todos."""
        completed_todos = sample_todos.get_todos(completed=True)
        assert len(completed_todos) == 1
        assert all(todo.completed for todo in completed_todos)

    def test_get_todos_pending(self, sample_todos: TodoManager) -> None:
        """Test getting only pending todos."""
        pending_todos = sample_todos.get_todos(completed=False)
        assert len(pending_todos) == 2
        assert all(not todo.completed for todo in pending_todos)

    def test_get_todo_by_id(self, sample_todos: TodoManager) -> None:
        """Test getting todo by ID."""
        todos = sample_todos.get_todos()
        first_todo = todos[0]

        found_todo = sample_todos.get_todo_by_id(first_todo.id)
        assert found_todo is first_todo

    def test_get_todo_by_nonexistent_id(self, sample_todos: TodoManager) -> None:
        """Test getting todo by nonexistent ID."""
        found_todo = sample_todos.get_todo_by_id(999)
        assert found_todo is None

    def test_complete_todo(self, todo_manager: TodoManager) -> None:
        """Test completing a todo."""
        todo = todo_manager.add_todo("Test todo")

        result = todo_manager.complete_todo(todo.id)

        assert result
        assert todo.completed

    def test_complete_nonexistent_todo(self, todo_manager: TodoManager) -> None:
        """Test completing nonexistent todo."""
        result = todo_manager.complete_todo(999)
        assert not result

    def test_complete_already_completed_todo(self, todo_manager: TodoManager) -> None:
        """Test completing already completed todo."""
        todo = todo_manager.add_todo("Test todo")
        todo.complete()

        result = todo_manager.complete_todo(todo.id)

        assert not result  # Should return False as it was already completed

    def test_uncomplete_todo(self, todo_manager: TodoManager) -> None:
        """Test uncompleting a todo."""
        todo = todo_manager.add_todo("Test todo")
        todo.complete()

        result = todo_manager.uncomplete_todo(todo.id)

        assert result
        assert not todo.completed

    def test_uncomplete_pending_todo(self, todo_manager: TodoManager) -> None:
        """Test uncompleting a pending todo."""
        todo = todo_manager.add_todo("Test todo")

        result = todo_manager.uncomplete_todo(todo.id)

        assert not result  # Should return False as it was already pending

    def test_delete_todo(self, todo_manager: TodoManager) -> None:
        """Test deleting a todo."""
        todo = todo_manager.add_todo("Test todo")
        todo_id = todo.id

        result = todo_manager.delete_todo(todo_id)

        assert result
        assert todo_manager.get_todo_by_id(todo_id) is None

    def test_delete_nonexistent_todo(self, todo_manager: TodoManager) -> None:
        """Test deleting nonexistent todo."""
        result = todo_manager.delete_todo(999)
        assert not result

    def test_clear_completed(self, sample_todos: TodoManager) -> None:
        """Test clearing completed todos."""
        # Should have 1 completed todo initially
        completed_before = sample_todos.get_todos(completed=True)
        assert len(completed_before) == 1

        count = sample_todos.clear_completed()

        assert count == 1
        completed_after = sample_todos.get_todos(completed=True)
        assert len(completed_after) == 0

    def test_clear_completed_none(self, todo_manager: TodoManager) -> None:
        """Test clearing completed todos when none exist."""
        todo_manager.add_todo("Pending todo")

        count = todo_manager.clear_completed()

        assert count == 0
        assert len(todo_manager.get_todos()) == 1

    @patch.object(TodoStorage, "save_todos")
    def test_save_called_on_modifications(
        self, mock_save: Mock, todo_manager: TodoManager
    ) -> None:
        """Test that save is called when todos are modified."""
        # Reset call count
        mock_save.reset_mock()

        # Operations that should trigger saves
        todo = todo_manager.add_todo("Test")
        todo_manager.complete_todo(todo.id)
        todo_manager.uncomplete_todo(todo.id)
        todo_manager.delete_todo(todo.id)

        # Should have been called for each operation
        assert mock_save.call_count == 4
