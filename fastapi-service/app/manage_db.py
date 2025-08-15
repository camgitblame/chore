#!/usr/bin/env python3
"""
Database management script to provide command-line interface to manage chores in the database.
"""

import sys
import json
from database import (
    init_database,
    get_all_chores,
    get_chore_by_id,
    add_chore,
    update_chore,
    delete_chore,
    search_chores,
)


def list_all_chores():
    """List all chores in the database."""
    chores = get_all_chores()
    if not chores:
        print("No chores found in database.")
        return

    print(f"\nFound {len(chores)} chores:")
    print("-" * 50)
    for chore in chores:
        print(f"ID: {chore['id']}")
        print(f"Title: {chore['title']}")
        print(f"Time: {chore['time_min']} minutes")
        print(f"Items: {', '.join(chore['items'])}")
        print(f"Steps: {len(chore['steps'])} steps")
        print("-" * 50)


def show_chore(chore_id):
    """Show detailed information about a specific chore."""
    chore = get_chore_by_id(chore_id)
    if not chore:
        print(f"Chore with ID '{chore_id}' not found.")
        return

    print(f"\nChore Details:")
    print(f"ID: {chore['id']}")
    print(f"Title: {chore['title']}")
    print(f"Estimated time: {chore['time_min']} minutes")
    print(f"\nRequired items:")
    for item in chore["items"]:
        print(f"  - {item}")
    print(f"\nSteps:")
    for i, step in enumerate(chore["steps"], 1):
        print(f"  {i}. {step}")


def search_chores_cmd(query):
    """Search for chores by title."""
    chores = search_chores(query)
    if not chores:
        print(f"No chores found matching '{query}'.")
        return

    print(f"\nFound {len(chores)} chores matching '{query}':")
    print("-" * 50)
    for chore in chores:
        print(f"ID: {chore['id']} - {chore['title']} ({chore['time_min']} min)")


def add_chore_interactive():
    """Add a new chore interactively."""
    print("\nAdding a new chore:")
    chore_id = input("Chore ID (unique identifier): ").strip()
    if not chore_id:
        print("Chore ID is required.")
        return

    # Check if chore already exists
    if get_chore_by_id(chore_id):
        print(f"Chore with ID '{chore_id}' already exists.")
        return

    title = input("Title: ").strip()
    if not title:
        print("Title is required.")
        return

    try:
        time_min = int(input("Estimated time (minutes): ").strip() or "0")
    except ValueError:
        time_min = 0

    print("Required items (enter one per line, empty line to finish):")
    items = []
    while True:
        item = input("  Item: ").strip()
        if not item:
            break
        items.append(item)

    print("Steps (enter one per line, empty line to finish):")
    steps = []
    while True:
        step = input("  Step: ").strip()
        if not step:
            break
        steps.append(step)

    chore_data = {
        "id": chore_id,
        "title": title,
        "items": items,
        "steps": steps,
        "time_min": time_min,
    }

    if add_chore(chore_data):
        print(f"Successfully added chore '{title}'!")
    else:
        print("Failed to add chore.")


def delete_chore_cmd(chore_id):
    """Delete a chore by ID."""
    chore = get_chore_by_id(chore_id)
    if not chore:
        print(f"Chore with ID '{chore_id}' not found.")
        return

    print(f"Are you sure you want to delete '{chore['title']}'? (y/N): ", end="")
    confirm = input().strip().lower()
    if confirm == "y":
        if delete_chore(chore_id):
            print(f"Successfully deleted chore '{chore['title']}'.")
        else:
            print("Failed to delete chore.")
    else:
        print("Deletion cancelled.")


def print_usage():
    """Print usage information."""
    print(
        """
Usage: python manage_db.py <command> [arguments]

Commands:
  list                 List all chores
  show <chore_id>      Show details of a specific chore
  search <query>       Search chores by title
  add                  Add a new chore interactively
  delete <chore_id>    Delete a chore
  init                 Initialize/reset database
  
Examples:
  python manage_db.py list
  python manage_db.py show microwave
  python manage_db.py search clean
  python manage_db.py add
  python manage_db.py delete old-chore
"""
    )


def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    # Initialize database if it doesn't exist
    init_database()

    if command == "list":
        list_all_chores()
    elif command == "show":
        if len(sys.argv) < 3:
            print("Usage: python manage_db.py show <chore_id>")
            return
        show_chore(sys.argv[2])
    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: python manage_db.py search <query>")
            return
        search_chores_cmd(sys.argv[2])
    elif command == "add":
        add_chore_interactive()
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Usage: python manage_db.py delete <chore_id>")
            return
        delete_chore_cmd(sys.argv[2])
    elif command == "init":
        print("Initializing database...")
        init_database()
        print("Database initialized!")
    else:
        print(f"Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main()
