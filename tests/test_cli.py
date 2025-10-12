"""Tests for the CLI interface.

This module demonstrates testing CLI applications using Click's testing framework
and comprehensive integration testing practices.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from click.testing import CliRunner

from todo_cli.cli import cli


class TestCLIBasic:
    """Test basic CLI functionality."""

    def test_cli_help(self, cli_runner: CliRunner) -> None:
        """Test CLI help message."""
        result = cli_runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Modern Todo CLI" in result.output
        assert "add" in result.output
        assert "list" in result.output
        assert "complete" in result.output

    def test_cli_version(self, cli_runner: CliRunner) -> None:
        """Test CLI version display."""
        result = cli_runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output


class TestAddCommand:
    """Test the add command."""

    def test_add_todo_with_title_only(
        self, isolated_cli_runner: tuple[CliRunner, Path]
    ) -> None:
        """Test adding todo with title only."""
        runner, storage_file = isolated_cli_runner

        result = runner.invoke(
            cli, ["--storage-file", str(storage_file), "add", "Learn Python"]
        )

        assert result.exit_code == 0
        assert "Added todo #1: Learn Python" in result.output

    def test_add_todo_with_description(
        self, isolated_cli_runner: tuple[CliRunner, Path]
    ) -> None:
        """Test adding todo with title and description."""
        runner, storage_file = isolated_cli_runner

        result = runner.invoke(
            cli,
            [
                "--storage-file",
                str(storage_file),
                "add",
                "Learn Python",
                "Study modern practices",
            ],
        )

        assert result.exit_code == 0
        assert re.search(r"Added todo #\d+: Learn Python", result.output)
        assert "Description: Study modern practices" in result.output

    def test_add_empty_title_error(
        self, isolated_cli_runner: tuple[CliRunner, Path]
    ) -> None:
        """Test adding todo with empty title shows error."""
        runner, storage_file = isolated_cli_runner

        result = runner.invoke(cli, ["--storage-file", str(storage_file), "add", ""])

        assert result.exit_code == 1
        assert "Error adding todo" in result.output

    def test_add_multiple_todos(
        self, isolated_cli_runner: tuple[CliRunner, Path]
    ) -> None:
        """Test adding multiple todos increments IDs."""

        runner, storage_file = isolated_cli_runner

        # Add first todo
        result1 = runner.invoke(
            cli,
            [
                "--storage-file",
                str(storage_file),
                "add",
                "First todo",
            ],
        )
        assert result1.exit_code == 0
        assert re.search(r"Added todo #\d+: First todo", result1.output)

        # Add second todo
        result2 = runner.invoke(
            cli, ["--storage-file", str(storage_file), "add", "Second todo"]
        )
        assert result2.exit_code == 0
        assert "Added todo #" in result2.output
        assert "Second todo" in result2.output


class TestListCommand:
    """Test the list command."""

    def test_list_empty(self, isolated_cli_runner: tuple[CliRunner, Path]) -> None:
        """Test listing when no todos exist."""
        runner, storage_file = isolated_cli_runner

        result = runner.invoke(cli, ["--storage-file", str(storage_file), "list"])

        assert result.exit_code == 0
        assert "No todos found" in result.output

    def test_list_todos_table_format(
        self, isolated_cli_runner: tuple[CliRunner, Path]
    ) -> None:
        """Test listing todos in table format (default)."""
        runner, storage_file = isolated_cli_runner

        # Add some todos first
        runner.invoke(
            cli,
            ["--storage-file", str(storage_file), "add", "First todo", "Description 1"],
        )
        runner.invoke(cli, ["--storage-file", str(storage_file), "add", "Second todo"])

        result = runner.invoke(cli, ["--storage-file", str(storage_file), "list"])

        assert result.exit_code == 0
        assert "First todo" in result.output
        assert "Second todo" in result.output
        assert "Description 1" in result.output
        # Table format should include headers
        assert "ID" in result.output
        assert "Status" in result.output

    def test_list_todos_simple_format(
        self, isolated_cli_runner: tuple[CliRunner, Path]
    ) -> None:
        """Test listing todos in simple format."""
        runner, storage_file = isolated_cli_runner

        # Add a todo first
        runner.invoke(cli, ["--storage-file", str(storage_file), "add", "Test todo"])

        result = runner.invoke(
            cli, ["--storage-file", str(storage_file), "list", "--format", "simple"]
        )

        assert result.exit_code == 0
        assert re.search(r"○ \[\d+\] Test todo", result.output)

    def test_list_completed_only(
        self, isolated_cli_runner: tuple[CliRunner, Path]
    ) -> None:
        """Test listing only completed todos."""
        runner, storage_file = isolated_cli_runner

        # Add and complete a todo
        result = runner.invoke(
            cli, ["--storage-file", str(storage_file), "add", "Completed todo"]
        )

        todo_id = re.findall(r"Added todo #(\d+): Completed todo", result.output)
        assert todo_id is not None
        runner.invoke(
            cli,
            ["--storage-file", str(storage_file), "complete", todo_id[0]],
        )
        runner.invoke(cli, ["--storage-file", str(storage_file), "add", "Pending todo"])

        result = runner.invoke(
            cli, ["--storage-file", str(storage_file), "list", "--completed", "true"]
        )

        assert result.exit_code == 0
        assert "Completed todo" in result.output
        assert "Pending todo" not in result.output

    def test_list_pending_only(
        self, isolated_cli_runner: tuple[CliRunner, Path]
    ) -> None:
        """Test listing only pending todos."""
        runner, storage_file = isolated_cli_runner

        # Add and complete a todo
        result = runner.invoke(
            cli, ["--storage-file", str(storage_file), "add", "Completed todo"]
        )
        todo_id = re.findall(r"Added todo #(\d+): Completed todo", result.output)
        assert todo_id is not None
        runner.invoke(
            cli,
            [
                "--storage-file",
                str(storage_file),
                "complete",
                todo_id[0],
            ],
        )
        runner.invoke(cli, ["--storage-file", str(storage_file), "add", "Pending todo"])

        result = runner.invoke(
            cli, ["--storage-file", str(storage_file), "list", "--completed", "false"]
        )

        assert result.exit_code == 0
        assert "Pending todo" in result.output
        assert "Completed todo" not in result.output


class TestCompleteCommand:
    """Test the complete command."""

    def test_complete_todo(self, isolated_cli_runner: tuple[CliRunner, Path]) -> None:
        """Test completing a todo."""
        runner, storage_file = isolated_cli_runner

        # Add a todo first
        result = runner.invoke(
            cli,
            [
                "--storage-file",
                str(storage_file),
                "add",
                "Test todo",
            ],
        )
        todo_id = re.findall(r"Added todo #(\d+): Test todo", result.output)
        assert todo_id is not None

        result = runner.invoke(
            cli, ["--storage-file", str(storage_file), "complete", todo_id[0]]
        )

        assert result.exit_code == 0
        assert f"Completed todo #{todo_id[0]}" in result.output

        # Verify it's marked as completed in list
        list_result = runner.invoke(
            cli,
            [
                "--storage-file",
                str(storage_file),
                "list",
                "--format",
                "simple",
            ],
        )
        assert f"✓ [{todo_id[0]}] Test todo" in list_result.output

    def test_complete_nonexistent_todo(
        self, isolated_cli_runner: tuple[CliRunner, Path]
    ) -> None:
        """Test completing nonexistent todo."""
        runner, storage_file = isolated_cli_runner

        result = runner.invoke(
            cli, ["--storage-file", str(storage_file), "complete", "999"]
        )

        assert result.exit_code == 1
        assert "Todo #999 not found" in result.output

    def test_complete_already_completed_todo(
        self, isolated_cli_runner: tuple[CliRunner, Path]
    ) -> None:
        """Test completing already completed todo."""
        runner, storage_file = isolated_cli_runner

        # Add and complete a todo
        result = runner.invoke(
            cli, ["--storage-file", str(storage_file), "add", "Test todo"]
        )
        todo_id = re.findall(r"Added todo #(\d+): Test todo", result.output)
        assert todo_id is not None
        runner.invoke(
            cli, ["--storage-file", str(storage_file), "complete", todo_id[0]]
        )

        # Try to complete again
        result = runner.invoke(
            cli,
            [
                "--storage-file",
                str(storage_file),
                "complete",
                todo_id[0],
            ],
        )

        assert result.exit_code == 1
        assert "already completed" in result.output


class TestUncompleteCommand:
    """Test the uncomplete command."""

    def test_uncomplete_todo(self, isolated_cli_runner: tuple[CliRunner, Path]) -> None:
        """Test uncompleting a todo."""
        runner, storage_file = isolated_cli_runner

        # Add and complete a todo
        result = runner.invoke(
            cli,
            [
                "--storage-file",
                str(storage_file),
                "add",
                "Test todo",
            ],
        )
        todo_id = re.findall(r"Added todo #(\d+): Test todo", result.output)
        assert todo_id is not None
        runner.invoke(
            cli,
            [
                "--storage-file",
                str(storage_file),
                "complete",
                todo_id[0],
            ],
        )

        result = runner.invoke(
            cli,
            [
                "--storage-file",
                str(storage_file),
                "uncomplete",
                todo_id[0],
            ],
        )

        assert result.exit_code == 0
        assert f"Marked todo #{todo_id[0]} as pending" in result.output

        # Verify it's marked as pending in list
        list_result = runner.invoke(
            cli, ["--storage-file", str(storage_file), "list", "--format", "simple"]
        )
        assert f"○ [{todo_id[0]}] Test todo" in list_result.output

    def test_uncomplete_nonexistent_todo(
        self, isolated_cli_runner: tuple[CliRunner, Path]
    ) -> None:
        """Test uncompleting nonexistent todo."""
        runner, storage_file = isolated_cli_runner

        result = runner.invoke(
            cli, ["--storage-file", str(storage_file), "uncomplete", "999"]
        )

        assert result.exit_code == 1
        assert "Todo #999 not found" in result.output


class TestDeleteCommand:
    """Test the delete command."""

    def test_delete_todo_with_confirmation(
        self, isolated_cli_runner: tuple[CliRunner, Path]
    ) -> None:
        """Test deleting a todo with confirmation."""
        runner, storage_file = isolated_cli_runner

        # Add a todo first
        result = runner.invoke(
            cli,
            [
                "--storage-file",
                str(storage_file),
                "add",
                "Test todo",
            ],
        )
        todo_id = re.findall(r"Added todo #(\d+): Test todo", result.output)
        assert todo_id is not None

        # Delete with confirmation
        result = runner.invoke(
            cli,
            ["--storage-file", str(storage_file), "delete", todo_id[0]],
            input="y\n",
        )

        assert result.exit_code == 0
        assert f"Deleted todo #{todo_id[0]}: Test todo" in result.output

        # Verify it's gone from list
        list_result = runner.invoke(cli, ["--storage-file", str(storage_file), "list"])
        assert "No todos found" in list_result.output

    def test_delete_todo_cancelled(
        self, isolated_cli_runner: tuple[CliRunner, Path]
    ) -> None:
        """Test cancelling todo deletion."""
        runner, storage_file = isolated_cli_runner

        # Add a todo first
        runner.invoke(cli, ["--storage-file", str(storage_file), "add", "Test todo"])

        # Delete but cancel
        result = runner.invoke(
            cli, ["--storage-file", str(storage_file), "delete", "1"], input="n\\n"
        )

        assert result.exit_code == 1  # Click abort returns 1

        # Verify todo still exists
        list_result = runner.invoke(cli, ["--storage-file", str(storage_file), "list"])
        assert "Test todo" in list_result.output

    def test_delete_nonexistent_todo(
        self, isolated_cli_runner: tuple[CliRunner, Path]
    ) -> None:
        """Test deleting nonexistent todo."""
        runner, storage_file = isolated_cli_runner

        result = runner.invoke(
            cli, ["--storage-file", str(storage_file), "delete", "999"], input="y\n"
        )

        assert result.exit_code == 1
        assert "Todo #999 not found" in result.output


class TestClearCompletedCommand:
    """Test the clear-completed command."""

    def test_clear_completed_todos(
        self, isolated_cli_runner: tuple[CliRunner, Path]
    ) -> None:
        """Test clearing completed todos."""
        runner, storage_file = isolated_cli_runner

        # Add and complete some todos
        result = runner.invoke(
            cli,
            [
                "--storage-file",
                str(storage_file),
                "add",
                "Todo 1",
            ],
        )
        todo_id = re.findall(r"Added todo #(\d+): Todo 1", result.output)
        assert todo_id is not None
        runner.invoke(
            cli,
            [
                "--storage-file",
                str(storage_file),
                "complete",
                todo_id[0],
            ],
        )

        result = runner.invoke(
            cli,
            [
                "--storage-file",
                str(storage_file),
                "add",
                "Todo 2",
            ],
        )
        todo_id = re.findall(r"Added todo #(\d+): Todo 2", result.output)
        assert todo_id is not None
        runner.invoke(
            cli,
            [
                "--storage-file",
                str(storage_file),
                "complete",
                todo_id[0],
            ],
        )

        runner.invoke(cli, ["--storage-file", str(storage_file), "add", "Todo 3"])
        result = runner.invoke(
            cli,
            [
                "--storage-file",
                str(storage_file),
                "clear-completed",
            ],
            input="y\n",
        )

        assert result.exit_code == 0
        assert re.search(
            r"Cleared \d+ completed todo\(s\)", result.output
        ), result.output

    def test_clear_completed_none(
        self, isolated_cli_runner: tuple[CliRunner, Path]
    ) -> None:
        """Test clearing completed when none exist."""
        runner, storage_file = isolated_cli_runner

        # Add pending todo
        runner.invoke(cli, ["--storage-file", str(storage_file), "add", "Pending todo"])

        result = runner.invoke(
            cli, ["--storage-file", str(storage_file), "clear-completed"], input="y\n"
        )

        assert result.exit_code == 0
        assert "No completed todos to clear" in result.output


class TestStatsCommand:
    """Test the stats command."""

    def test_stats_empty(self, isolated_cli_runner: tuple[CliRunner, Path]) -> None:
        """Test stats with no todos."""
        runner, storage_file = isolated_cli_runner

        result = runner.invoke(cli, ["--storage-file", str(storage_file), "stats"])

        assert result.exit_code == 0
        assert "Total todos: 0" in result.output
        assert "Completed: 0" in result.output
        assert "Pending: 0" in result.output
        assert "Completion rate" not in result.output  # No rate when no todos

    def test_stats_with_todos(
        self, isolated_cli_runner: tuple[CliRunner, Path]
    ) -> None:
        """Test stats with mixed todos."""
        runner, storage_file = isolated_cli_runner

        # Add and complete some todos
        result = runner.invoke(
            cli,
            [
                "--storage-file",
                str(storage_file),
                "add",
                "Todo 1",
            ],
        )
        todo_id = re.findall(r"Added todo #(\d+): Todo 1", result.output)
        assert todo_id is not None
        runner.invoke(
            cli,
            [
                "--storage-file",
                str(storage_file),
                "complete",
                todo_id[0],
            ],
        )

        runner.invoke(cli, ["--storage-file", str(storage_file), "add", "Todo 2"])
        runner.invoke(cli, ["--storage-file", str(storage_file), "add", "Todo 3"])

        result = runner.invoke(cli, ["--storage-file", str(storage_file), "stats"])

        assert result.exit_code == 0
        assert "Total todos: 3" in result.output
        assert "Completed: 1" in result.output
        assert "Pending: 2" in result.output
        assert "Completion rate: 33.3%" in result.output


class TestStorageFileOption:
    """Test the --storage-file option."""

    def test_custom_storage_file(
        self, cli_runner: CliRunner, temp_storage_file: Path
    ) -> None:
        """Test using custom storage file."""
        # Add todo to custom file
        result1 = cli_runner.invoke(
            cli,
            ["--storage-file", str(temp_storage_file), "add", "Custom storage todo"],
        )
        assert result1.exit_code == 0

        # Verify it's stored in the custom file
        assert temp_storage_file.exists()
        data = json.loads(temp_storage_file.read_text())
        assert len(data) == 1
        assert data[0]["title"] == "Custom storage todo"

        # Verify it can be loaded from custom file
        result2 = cli_runner.invoke(
            cli,
            ["--storage-file", str(temp_storage_file), "list", "--format", "simple"],
        )
        assert result2.exit_code == 0
        assert "Custom storage todo" in result2.output


class TestErrorHandling:
    """Test error handling in the CLI."""

    def test_invalid_todo_id_type(
        self, isolated_cli_runner: tuple[CliRunner, Path]
    ) -> None:
        """Test providing invalid todo ID type."""
        runner, storage_file = isolated_cli_runner

        result = runner.invoke(
            cli, ["--storage-file", str(storage_file), "complete", "not-a-number"]
        )

        assert result.exit_code != 0

    def test_missing_required_argument(
        self, isolated_cli_runner: tuple[CliRunner, Path]
    ) -> None:
        """Test missing required argument."""
        runner, storage_file = isolated_cli_runner

        result = runner.invoke(cli, ["--storage-file", str(storage_file), "add"])

        assert result.exit_code != 0
        assert "Missing argument" in result.output.lower() or "Usage:" in result.output
