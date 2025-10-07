"""Todo item data models and business logic."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar


@dataclass
class TodoItem:
    """Represents a single todo item.

    This class demonstrates modern Python practices:
    - Dataclasses for clean data modeling
    - Type hints for better code documentation
    - Immutable design with frozen=True option available
    - Proper __post_init__ usage for validation
    """

    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(
        default_factory=datetime.now,
    )
    completed_at: datetime | None = None
    id: int = field(default=0, init=False)

    # Class variable for auto-incrementing IDs
    _next_id: ClassVar[int] = 1

    def __post_init__(self) -> None:
        """Initialize the todo item after creation."""
        if not self.title.strip():
            raise ValueError("Todo title cannot be empty")

        # Auto-assign ID if not set
        if self.id == 0:
            self.id = TodoItem._next_id
            TodoItem._next_id += 1

    def complete(self) -> None:
        """Mark the todo as completed."""
        if not self.completed:
            self.completed = True
            self.completed_at = datetime.now()

    def uncomplete(self) -> None:
        """Mark the todo as not completed."""
        if self.completed:
            self.completed = False
            self.completed_at = None

    def to_dict(self) -> dict[str, Any]:
        """Convert todo item to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TodoItem:
        """Create todo item from dictionary (JSON deserialization)."""
        # Update the next_id counter to avoid conflicts
        if data["id"] >= cls._next_id:
            cls._next_id = data["id"] + 1

        item = cls(
            title=data["title"],
            description=data.get("description", ""),
            completed=data.get("completed", False),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
        item.id = data["id"]

        if data.get("completed_at"):
            item.completed_at = datetime.fromisoformat(data["completed_at"])

        return item


class TodoStorage:
    """Handles persistence of todo items to JSON file.

    This class demonstrates:
    - Separation of concerns (storage vs business logic)
    - Proper error handling
    - Context manager pattern usage
    - Pathlib for modern file path handling
    """

    def __init__(self, file_path: Path | str = "todos.json") -> None:
        """Initialize storage with file path."""
        self.file_path = Path(file_path)

    def load_todos(self) -> list[TodoItem]:
        """Load all todos from storage file."""
        if not self.file_path.exists():
            return []

        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return [TodoItem.from_dict(item_data) for item_data in data]
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise RuntimeError(
                f"Failed to load todos from {self.file_path}: {e}"
            ) from e

    def save_todos(self, todos: list[TodoItem]) -> None:
        """Save all todos to storage file."""
        try:
            # Ensure parent directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            with self.file_path.open("w", encoding="utf-8") as f:
                json.dump(
                    [todo.to_dict() for todo in todos],
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
        except (OSError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to save todos to {self.file_path}: {e}") from e


class TodoManager:
    """Manages todo items and coordinates with storage.

    This class provides the main business logic and demonstrates:
    - Single Responsibility Principle
    - Dependency injection (storage)
    - Comprehensive error handling
    - Modern Python typing
    """

    def __init__(self, storage: TodoStorage | None = None) -> None:
        """Initialize manager with optional storage backend."""
        self.storage = storage or TodoStorage()
        self._todos: list[TodoItem] = []
        self.load()

    def load(self) -> None:
        """Load todos from storage."""
        self._todos = self.storage.load_todos()

    def save(self) -> None:
        """Save todos to storage."""
        self.storage.save_todos(self._todos)

    def add_todo(self, title: str, description: str = "") -> TodoItem:
        """Add a new todo item."""
        todo = TodoItem(title=title, description=description)
        self._todos.append(todo)
        self.save()
        return todo

    def get_todos(self, completed: bool | None = None) -> list[TodoItem]:
        """Get todos, optionally filtered by completion status."""
        if completed is None:
            return self._todos.copy()
        return [todo for todo in self._todos if todo.completed == completed]

    def get_todo_by_id(self, todo_id: int) -> TodoItem | None:
        """Get a specific todo by ID."""
        return next((todo for todo in self._todos if todo.id == todo_id), None)

    def complete_todo(self, todo_id: int) -> bool:
        """Mark a todo as completed."""
        todo = self.get_todo_by_id(todo_id)
        if todo and not todo.completed:
            todo.complete()
            self.save()
            return True
        return False

    def uncomplete_todo(self, todo_id: int) -> bool:
        """Mark a todo as not completed."""
        todo = self.get_todo_by_id(todo_id)
        if todo and todo.completed:
            todo.uncomplete()
            self.save()
            return True
        return False

    def delete_todo(self, todo_id: int) -> bool:
        """Delete a todo by ID."""
        todo = self.get_todo_by_id(todo_id)
        if todo:
            self._todos.remove(todo)
            self.save()
            return True
        return False

    def clear_completed(self) -> int:
        """Remove all completed todos and return count of removed items."""
        completed_todos = [todo for todo in self._todos if todo.completed]
        self._todos = [todo for todo in self._todos if not todo.completed]
        if completed_todos:
            self.save()
        return len(completed_todos)
