# db

`aiomql.core.db` — SQLite ORM base class with dataclass support.

## Overview

The `DB` class provides ORM-style CRUD operations backed by SQLite. Classes that inherit
from `DB` and are decorated with `@dataclass` automatically get a database table whose
columns mirror the dataclass fields. Column types, defaults, and constraints (e.g.
`PRIMARY KEY`) are derived from field metadata.

## Classes

### `DB`

> Base class for ORM-style database operations.

| Class Attribute | Type | Description |
|-----------------|------|-------------|
| `table_name` | `ClassVar[str]` | Table name (defaults to class name) |

#### Schema Helpers

| Method | Description |
|--------|-------------|
| `pk` *(property)* | Returns `(field_name, value)` for the PRIMARY KEY field |
| `init_db()` | Initialises the connection and creates the table |
| `get_connection()` | Returns a new `sqlite3.Connection` with a custom row factory |
| `create_table(conn)` | Creates the table if it doesn't exist |
| `get_columns()` | Generates column definitions from dataclass fields |
| `types(key)` | Maps a Python type to its SQLite equivalent |
| `get_default(col)` | Returns the `DEFAULT` SQL clause for a field |
| `get_metadata(col)` | Extracts SQL constraints (e.g. `PRIMARY KEY`) from field metadata |
| `dict_factory()` | Returns a row factory that converts rows into class instances |
| `sanitize(identifier)` | Sanitises a SQL identifier to prevent injection |

#### CRUD Operations

| Method | Description |
|--------|-------------|
| `save(commit=True, update=False, data=None, conn=None)` | Inserts or updates a record |
| `get(**kwargs)` | Returns the first matching record, or `None` |
| `filter(**kwargs)` | Returns all matching records (or all if no criteria) |
| `clear()` | Deletes all records from the table |

#### Serialisation

| Method | Description |
|--------|-------------|
| `asdict()` | Converts the instance to a dictionary |
| `get_data()` | Returns instance data for saving |
