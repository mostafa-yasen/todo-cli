"""CLI interface for the todo application.

This module demonstrates modern CLI development practices:
- Click framework for robust command-line interfaces
- Rich library for beautiful terminal output
- Type hints throughout
- Proper error handling and user feedback
- Command grouping and help text
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text

from todo_cli.models import TodoManager, TodoStorage

# Global console instance for rich output
console = Console()


def create_todo_table(todos: list[Any]) -> Table:
    """Create a rich table for displaying todos."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=4)
    table.add_column("Status", width=8)
    table.add_column("Title", style="bold")
    table.add_column("Description")
    table.add_column("Created", style="dim")

    for todo in todos:
        status_text = (
            Text("✓ Done", style="green")
            if todo.completed
            else Text("○ Pending", style="yellow")
        )
        created_date = todo.created_at.strftime("%Y-%m-%d %H:%M")

        table.add_row(
            str(todo.id),
            status_text,
            todo.title,
            todo.description or "-",
            created_date,
        )

    return table


def get_todo_manager(storage_file: str | None = None) -> TodoManager:
    """Get a configured TodoManager instance."""
    if storage_file:
        storage = TodoStorage(Path(storage_file))
        return TodoManager(storage)
    return TodoManager()


@click.group()
@click.version_option(version="0.1.0", prog_name="todo-cli")
@click.option(
    "--storage-file",
    type=click.Path(),
    help="Path to the todo storage file (default: todos.json)",
)
@click.pass_context
def cli(ctx: click.Context, storage_file: str | None = None) -> None:
    """Modern Todo CLI - A blueprint for Python CLI applications.

    This tool demonstrates modern Python development practices including:
    - Project structure with src/ layout
    - Dependency management with uv and pyproject.toml
    - Type hints and dataclasses
    - Comprehensive testing with pytest
    - Beautiful CLI with Click and Rich

    Examples:
      todo add "Learn Python" "Study modern Python practices"
      todo list
      todo complete 1
      todo delete 1
    """
    ctx.ensure_object(dict)
    ctx.obj["storage_file"] = storage_file


@cli.command()
@click.argument("title", required=True)
@click.argument("description", required=False, default="")
@click.pass_context
def add(ctx: click.Context, title: str, description: str) -> None:
    """Add a new todo item.

    TITLE: The todo title (required)
    DESCRIPTION: Optional description for the todo

    Examples:
      todo add "Buy groceries"
      todo add "Finish project" "Complete the final report and review"
    """
    try:
        manager = get_todo_manager(ctx.obj["storage_file"])
        todo = manager.add_todo(title, description)

        console.print(f"✓ Added todo #{todo.id}: [bold]{title}[/bold]", style="green")
        if description:
            console.print(f"  Description: {description}", style="dim")

    except Exception as e:
        console.print(f"Error adding todo: {e}", style="red")
        sys.exit(1)


@cli.command("list")
@click.option(
    "--completed",
    type=click.Choice(["true", "false"]),
    help="Filter by completion status",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "simple"]),
    default="table",
    help="Output format",
)
@click.pass_context
def list_todos(
    ctx: click.Context, completed: str | None = None, output_format: str = "table"
) -> None:
    """List all todo items.

    Use --completed to filter by status:
      todo list --completed true    (show only completed)
      todo list --completed false   (show only pending)
      todo list                     (show all)
    """
    try:
        manager = get_todo_manager(ctx.obj["storage_file"])

        # Convert string to boolean for filtering
        completed_filter = None
        if completed == "true":
            completed_filter = True
        elif completed == "false":
            completed_filter = False

        todos = manager.get_todos(completed=completed_filter)

        if not todos:
            console.print("No todos found.", style="yellow")
            return

        if output_format == "table":
            table = create_todo_table(todos)
            console.print(table)
        else:
            # Simple format
            for todo in todos:
                status = "✓" if todo.completed else "○"
                console.print(f"{status} [{todo.id}] {todo.title}")
                if todo.description:
                    console.print(f"    {todo.description}", style="dim")

    except Exception as e:
        console.print(f"Error listing todos: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.argument("todo_id", type=int, required=True)
@click.pass_context
def complete(ctx: click.Context, todo_id: int) -> None:
    """Mark a todo as completed.

    TODO_ID: The ID of the todo to complete

    Example:
      todo complete 1
    """
    try:
        manager = get_todo_manager(ctx.obj["storage_file"])

        if manager.complete_todo(todo_id):
            console.print(f"✓ Completed todo #{todo_id}", style="green")
        else:
            todo = manager.get_todo_by_id(todo_id)
            if todo is None:
                console.print(f"Todo #{todo_id} not found", style="red")
            else:
                console.print(f"Todo #{todo_id} is already completed", style="yellow")
            sys.exit(1)

    except Exception as e:
        console.print(f"Error completing todo: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.argument("todo_id", type=int, required=True)
@click.pass_context
def uncomplete(ctx: click.Context, todo_id: int) -> None:
    """Mark a completed todo as pending.

    TODO_ID: The ID of the todo to mark as pending

    Example:
      todo uncomplete 1
    """
    try:
        manager = get_todo_manager(ctx.obj["storage_file"])

        if manager.uncomplete_todo(todo_id):
            console.print(f"○ Marked todo #{todo_id} as pending", style="yellow")
        else:
            todo = manager.get_todo_by_id(todo_id)
            if todo is None:
                console.print(f"Todo #{todo_id} not found", style="red")
            else:
                console.print(f"Todo #{todo_id} is already pending", style="yellow")
            sys.exit(1)

    except Exception as e:
        console.print(f"Error updating todo: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.argument("todo_id", type=int, required=True)
@click.confirmation_option(prompt="Are you sure you want to delete this todo?")
@click.pass_context
def delete(ctx: click.Context, todo_id: int) -> None:
    """Delete a todo item.

    TODO_ID: The ID of the todo to delete

    Example:
      todo delete 1
    """
    try:
        manager = get_todo_manager(ctx.obj["storage_file"])

        # Get todo details before deletion for confirmation message
        todo = manager.get_todo_by_id(todo_id)
        if todo is None:
            console.print(f"Todo #{todo_id} not found", style="red")
            sys.exit(1)

        if manager.delete_todo(todo_id):
            console.print(
                f"✗ Deleted todo #{todo_id}: [bold]{todo.title}[/bold]", style="red"
            )
        else:
            console.print(f"Failed to delete todo #{todo_id}", style="red")
            sys.exit(1)

    except click.Abort:
        console.print("Deletion cancelled.", style="yellow")
    except Exception as e:
        console.print(f"Error deleting todo: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.confirmation_option(prompt="Are you sure you want to clear all completed todos?")
@click.pass_context
def clear_completed(ctx: click.Context) -> None:
    """Clear all completed todos.

    This will permanently delete all todos marked as completed.

    Example:
      todo clear-completed
    """
    try:
        manager = get_todo_manager(ctx.obj["storage_file"])

        count = manager.clear_completed()
        if count > 0:
            console.print(f"✗ Cleared {count} completed todo(s)", style="green")
        else:
            console.print("No completed todos to clear", style="yellow")

    except click.Abort:
        console.print("Clear operation cancelled.", style="yellow")
    except Exception as e:
        console.print(f"Error clearing completed todos: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.pass_context
def stats(ctx: click.Context) -> None:
    """Show todo statistics.

    Display summary statistics about your todos.

    Example:
      todo stats
    """
    try:
        manager = get_todo_manager(ctx.obj["storage_file"])

        all_todos = manager.get_todos()
        completed_todos = manager.get_todos(completed=True)
        pending_todos = manager.get_todos(completed=False)

        console.print("\n[bold]Todo Statistics[/bold]")
        console.print("─" * 20)
        console.print(f"Total todos: [bold]{len(all_todos)}[/bold]")
        console.print(f"Completed: [green]{len(completed_todos)}[/green]")
        console.print(f"Pending: [yellow]{len(pending_todos)}[/yellow]")

        if all_todos:
            completion_rate = (len(completed_todos) / len(all_todos)) * 100
            console.print(f"Completion rate: [cyan]{completion_rate:.1f}%[/cyan]")

        console.print()

    except Exception as e:
        console.print(f"Error getting statistics: {e}", style="red")
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI application."""
    cli()


if __name__ == "__main__":
    main()
