#!/usr/bin/env python3
"""
Database initialization script to set up the SQLite database.
"""

from database import init_database, add_chore


def add_sample_chores():
    """Add some additional sample chores to the database."""
    sample_chores = [
        {
            "id": "bathroom",
            "title": "Quick bathroom clean",
            "items": [
                "All-purpose cleaner",
                "Toilet brush",
                "Microfiber cloth",
                "Glass cleaner",
            ],
            "steps": [
                "Spray all-purpose cleaner on surfaces",
                "Wipe down sink, counter, and toilet exterior",
                "Clean toilet bowl with brush",
                "Clean mirror with glass cleaner",
                "Sweep or vacuum floor",
            ],
            "time_min": 15,
        },
        {
            "id": "kitchen-counter",
            "title": "Clear kitchen counter",
            "items": ["Dish soap", "Sponge", "All-purpose cleaner", "Dish towel"],
            "steps": [
                "Put away items that don't belong on counter",
                "Load dirty dishes into dishwasher",
                "Wipe down counter with cleaner",
                "Clean and put away any remaining items",
                "Dry counter with clean towel",
            ],
            "time_min": 12,
        },
        {
            "id": "make-bed",
            "title": "Make the bed",
            "items": [],
            "steps": [
                "Pull sheets and blankets up to head of bed",
                "Smooth out wrinkles",
                "Arrange pillows neatly",
                "Fold back comforter or duvet nicely",
                "Fluff and arrange decorative pillows if any",
            ],
            "time_min": 3,
        },
    ]

    for chore in sample_chores:
        add_chore(chore)
        print(f"Added chore: {chore['title']}")


if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    print("Database initialized successfully!")

    print("\nAdding sample chores...")
    add_sample_chores()
    print("Sample chores added!")

    print("\nDatabase setup complete!")
