# Chore Coach Database Migration

This document describes the migration from hard-coded chore data to a SQLite database system.

## Changes Made

### 1. Database Module (`fastapi-service/app/database.py`)

Created a comprehensive database module with the following features:

- **SQLite Integration**: Uses SQLite for lightweight, file-based data storage
- **Automatic Initialization**: Creates database and tables on first run
- **Data Persistence**: Stores chores with ID, title, items, steps, and time estimates
- **JSON Storage**: Items and steps are stored as JSON arrays for flexibility

#### Key Functions:
- `init_database()`: Initialize database and populate with default chores
- `get_all_chores()`: Retrieve all chores
- `get_chore_by_id(chore_id)`: Get a specific chore
- `search_chores(query)`: Search chores by title
- `add_chore(chore_data)`: Add a new chore
- `update_chore(chore_id, chore_data)`: Update existing chore
- `delete_chore(chore_id)`: Delete a chore

### 2. Updated Main Application (`fastapi-service/app/main.py`)

Modified the FastAPI application to use the database:

- **Removed Hard-coded Data**: Eliminated the `CHORES` list
- **Database Integration**: Uses database functions for all chore operations
- **Backward Compatibility**: API endpoints remain the same
- **Automatic Initialization**: Database is initialized on startup

### 3. Management Tools

Created several utility scripts for database management:

#### `fastapi-service/app/init_db.py`
- Standalone database initialization script
- Adds sample chores beyond the default ones
- Can be run independently to set up the database

#### `fastapi-service/app/manage_db.py`
- Command-line interface for database management
- Commands: `list`, `show`, `search`, `add`, `delete`, `init`
- Interactive chore creation
- Safe deletion with confirmation

#### `test_database.py`
- Comprehensive test suite for database functions
- API endpoint simulation
- Verifies all CRUD operations

## Database Schema

```sql
CREATE TABLE chores (
    id TEXT PRIMARY KEY,           -- Unique identifier
    title TEXT NOT NULL,           -- Chore title
    items TEXT,                    -- JSON array of required items
    steps TEXT,                    -- JSON array of steps
    time_min INTEGER               -- Estimated time in minutes
);
```

## Usage Examples

### Start the Application
```bash
cd fastapi-service
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

### Manage Database
```bash
cd fastapi-service/app
python3 manage_db.py list                    # List all chores
python3 manage_db.py show microwave          # Show specific chore
python3 manage_db.py search clean            # Search chores
python3 manage_db.py add                     # Add new chore interactively
python3 manage_db.py delete old-chore        # Delete a chore
```

### Test Database
```bash
python3 test_database.py                     # Run comprehensive tests
```

## API Endpoints (Unchanged)

The following API endpoints work exactly as before:

- `GET /chores` - List all chores (with optional search query)
- `GET /chores/{chore_id}` - Get specific chore details
- `POST /tts` - Text-to-speech generation for chores

## Benefits of This Migration

1. **Persistence**: Data survives application restarts
2. **Scalability**: Easy to add/modify chores without code changes
3. **Management**: Command-line tools for easy administration
4. **Flexibility**: JSON storage allows complex data structures
5. **Performance**: SQLite provides efficient querying and indexing
6. **Maintainability**: Clear separation of data and business logic

## Migration Notes

- **No Breaking Changes**: Existing API clients continue to work
- **Automatic Migration**: First run populates database with original chores
- **File Location**: Database stored as `chores.db` in the app directory
- **Backup**: Database file can be easily backed up or migrated

## Future Enhancements

Possible future improvements include:

- User-specific chore lists
- Chore completion tracking
- Categories and tags
- Chore scheduling
- Multi-language support
- Image attachments for chores
