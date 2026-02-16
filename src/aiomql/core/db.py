"""Database ORM module for SQLite operations with dataclass support.

This module provides the DB class, a base class for ORM-style database
operations. Classes that inherit from DB and are decorated with @dataclass
automatically get table creation, CRUD operations, and serialization.

The DB class maps Python types to SQLite types and uses dataclass fields
to define table columns.

Example:
    Creating a model class::

        from dataclasses import dataclass
        from aiomql.core.db import DB

        @dataclass
        class TradeRecord(DB):
            symbol: str
            volume: float
            profit: float

        # Save a record
        record = TradeRecord(symbol='EURUSD', volume=0.1, profit=50.0)
        record.save()

        # Query records
        trades = TradeRecord.filter(symbol='EURUSD')
"""

import os
import sqlite3
import re
from logging import getLogger
from dataclasses import Field, fields, asdict, MISSING, is_dataclass
from typing import ClassVar
from functools import cached_property

from .config import Config

logger = getLogger(__name__)

class DB:
    """A base class for ORM-style database operations with SQLite.

    Designed to be used with @dataclass decorator. Provides automatic
    table creation based on dataclass fields, and CRUD operations.

    Attributes:
        _table (ClassVar[str]): The database table name. Defaults to
            lowercase class name.
        _initialized (ClassVar[bool]): Whether the database has been
            initialized for this class.
        TYPES (ClassVar[dict]): Mapping of Python types to SQLite types.
        config (ClassVar[Config]): The global configuration instance.
        db_name (ClassVar[str]): The database file name.

    Example:
        >>> @dataclass
        ... class User(DB):
        ...     name: str
        ...     age: int
        >>> user = User(name='John', age=30)
        >>> user.save()
    """

    _table: ClassVar[str] = ""
    _initialized: ClassVar[bool] = False
    TYPES: ClassVar[dict] = {str: "TEXT", float: "REAL", int: "INTEGER", bool: "BOOLEAN", None: "NULL", bytes: "BLOB"}
    config: ClassVar[Config]
    db_name: ClassVar[str]

    def __new__(cls, *args, **kwargs):
        """Creates a new instance and initializes the Config.

        Returns:
            DB: A new instance of the class.
        """
        cls.config = Config()
        if not cls._initialized:
            cls.init_db()
        return super().__new__(cls)

    # def __post_init__(self):
    #     """Called after dataclass __init__ to initialize the database."""
    #     self.init_db()

    @cached_property
    def pk(self):
        """Returns the primary key field name and value.

        Searches through the dataclass fields to find the one marked with
        the 'PRIMARY KEY' metadata flag.

        Returns:
            tuple[str, Any]: A tuple containing the primary key field name
                and its current value.

        Raises:
            StopIteration: If no field is marked with PRIMARY KEY metadata.
        """
        name = next((f.name for f in fields(self) if f.metadata.get("PRIMARY KEY")))
        return name, getattr(self, name)

    @classmethod
    def init_db(cls):
        """Initializes the database connection and creates the table.

        Sets up the SQLite connection with a custom row factory and
        creates the table if it doesn't exist.
        """
        cls.config = Config()
        cls.db_name = getattr(cls.config, "db_name", os.getenv("DB_NAME", "db.sqlite3"))
        conn = sqlite3.connect(cls.db_name)
        cls.create_table(conn)
        conn.close()
    
    @classmethod
    def get_connection(cls):
        """Gets a new database connection.

        Initializes the database if not already done, then creates and
        returns a new SQLite connection with the custom row factory.

        Returns:
            sqlite3.Connection: A new database connection with the
                class's dict_factory set as the row factory.
        """
        if not cls._initialized:
            cls.init_db()
            cls._initialized = True
        conn = sqlite3.connect(cls.db_name)
        conn.row_factory = cls.dict_factory()
        return conn

    @classmethod
    def create_table(cls, conn: sqlite3.Connection):
        """Creates the database table if it doesn't exist.

        Uses the dataclass fields to determine column definitions.

        Args:
            conn: The database connection to use.
        """
        try:
            if not is_dataclass(cls):
                return
            cls._table = cls._table or cls.__name__.lower()
            columns = cls.get_columns()
            conn.execute(f"""CREATE TABLE IF NOT EXISTS'{cls._table}' ({columns})""")
            conn.commit()
            cls._initialized = True
        except Exception as e:
            logger.error("%s: Failed to create table", e)

    @classmethod
    def dict_factory(cls):
        """Creates a row factory that returns class instances.

        Returns:
            Callable: A factory function for SQLite row conversion.
        """
        def dict_factory(cursor, row):
            cols = [column[0] for column in cursor.description]
            kw = {key: value for key, value in zip(cols, row)}
            return cls(**kw)
        return dict_factory

    @staticmethod
    def sanitize(identifier):
        """Sanitizes a SQL identifier to prevent injection.

        Args:
            identifier: The table or column name to sanitize.

        Returns:
            str: The sanitized identifier wrapped in quotes.

        Raises:
            ValueError: If the identifier contains invalid characters.
        """
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", identifier):
            return f'"{identifier}"'
        raise ValueError("Invalid table name")

    @classmethod
    def types(cls, key):
        """Maps a Python type to its SQLite equivalent.

        Args:
            key: The Python type to map.

        Returns:
            str: The corresponding SQLite type. Defaults to TEXT.
        """
        return cls.TYPES.get(key, "TEXT")

    @staticmethod
    def get_default(col: Field):
        """Gets the DEFAULT clause for a dataclass field.

        Args:
            col: The dataclass Field to get the default for.

        Returns:
            str: The DEFAULT SQL clause, or empty string if no default.
        """
        if isinstance(col.default, type(MISSING)) and isinstance(col.default_factory, type(MISSING)):
            return ""

        if not isinstance(col.default, type(MISSING)):
            return f"DEFAULT {col.default!r}"

        if not isinstance(col.default_factory, type(MISSING)):
            return f"DEFAULT {col.default_factory()!r}"

        return ""

    @staticmethod
    def get_metadata(col: Field):
        """Extracts SQL metadata from a dataclass field.

        Args:
            col: The dataclass Field to extract metadata from.

        Returns:
            str: SQL constraints from field metadata (e.g., PRIMARY KEY).
        """
        return f"{' '.join(meta for meta, value in col.metadata.items() if value)}"

    @classmethod
    def get_columns(cls):
        """Generates the column definitions for table creation.

        Returns:
            str: Comma-separated column definitions for CREATE TABLE.
        """
        cols = fields(cls)
        cols = [f"'{col.name}' {cls.types(col.type)} {cls.get_metadata(col)} {cls.get_default(col)}" for col in
                cols]
        return ",".join(cols)

    def asdict(self):
        """Converts the instance to a dictionary.

        Returns:
            dict: The dataclass fields as a dictionary.
        """
        return asdict(self)

    def get_data(self):
        """Returns the instance data for saving.

        Returns:
            dict: The instance data as a dictionary.
        """
        return self.asdict()

    @classmethod
    def clear(cls):
        """Deletes all records from the table.

        Removes all rows from the model's table. The table structure
        remains intact.

        Note:
            This operation is irreversible. Use with caution.
        """
        conn = cls.get_connection()
        conn.execute(f"DELETE FROM {cls._table}")
        conn.commit()
        conn.close()

    def save(self, commit: bool = True, update: bool = False, data: dict = None, conn: sqlite3.Connection = None):
        """Saves the current instance to the database.

        Inserts a new record or updates an existing one based on the
        update parameter. Uses parameterized queries for safety.

        Args:
            commit: If True, commits the transaction and closes the
                connection. Defaults to True.
            update: If True, performs an UPDATE using the primary key.
                If False, performs an INSERT. Defaults to False.
            data: Dictionary of field-value pairs to save. If None,
                uses get_data() to retrieve instance data.
            conn: An existing database connection to use. If None,
                creates a new connection.

        Example:
            >>> record = TradeRecord(symbol='EURUSD', volume=0.1)
            >>> record.save()  # Insert new record
            >>> record.volume = 0.2
            >>> record.save(update=True)  # Update existing record
        """
        conn = conn or self.get_connection()
        data = data or self.get_data()
        columns = ", ".join(self.sanitize(key) for key in data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = tuple(data.values())
        table = self.sanitize(self._table)
        if update:
            pk, pk_value = self.pk
            update_columns = ", ".join(f"{self.sanitize(key)} = ?" for key in data.keys())
            query = f"UPDATE {table} SET {update_columns} WHERE {self.sanitize(pk)} = {pk_value}"
        else:
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        conn.execute(query, values)
        if commit:
            conn.commit()
            conn.close()

    @classmethod
    def get(cls, **kwargs):
        """Retrieves a single record matching the criteria.

        Args:
            **kwargs: Field-value pairs to filter by.

        Returns:
            The first matching record as a class instance, or None.
        """
        conn = cls.get_connection()
        _query = " AND ".join([f'"{key}" = "{value}"' for key, value in kwargs.items()])
        query = f"""SELECT * FROM {cls.sanitize(cls._table)} WHERE {_query}"""
        res = conn.execute(query).fetchone()
        conn.close()
        return res

    @classmethod
    def filter(cls, **kwargs):
        """Retrieves all records matching the criteria.

        Args:
            **kwargs: Field-value pairs to filter by. If empty, returns all.

        Returns:
            list: Matching records as class instances.
        """
        conn = cls.get_connection()
        _query = " AND ".join([f'"{key}" = "{value}"' for key, value in kwargs.items()])
        _query = f"WHERE {_query}" if _query else ""
        query = f"SELECT * FROM {cls.sanitize(cls._table)} {_query}"
        res = conn.execute(query).fetchall()
        conn.close()
        return res

    @classmethod
    def update(cls, data=None, /, **kwargs):
        """Updates records matching the criteria.

        Args:
            data: Dictionary of field-value pairs to update.
            **kwargs: Field-value pairs to filter which records to update.

        Returns:
            bool: True if the update was successful.
        """
        conn = cls.get_connection()
        update = data or {}
        _query = " AND ".join([f'"{key}" = "{value}"' for key, value in kwargs.items()])
        update = ", ".join([f'"{key}" = "{value}"' for key, value in update.items()])
        table = cls.sanitize(cls._table)
        _query = f"WHERE {_query}" if _query else ""
        query = f"""UPDATE {table} SET {update} {_query}"""
        conn.execute(query)
        conn.commit()
        conn.close()
        return True

    @classmethod
    def fields(cls) -> list[str]:
        """Returns a list of field names for the model.

        Returns:
            list[str]: The names of all dataclass fields.
        """
        fs = fields(cls)
        return [f.name for f in fs]

    @classmethod
    def drop_table(cls):
        """Drops the database table if it exists.

        Permanently removes the table and all its data from the database.
        This is a destructive operation.

        Note:
            This operation is irreversible. All data in the table
            will be permanently deleted.
        """
        conn = cls.get_connection()
        conn.execute(f"DROP TABLE IF EXISTS {cls._table}")
        conn.commit()
        conn.close()


    @classmethod
    def all(cls, limit: int | None = None):
        """Returns all records from the table.

        Retrieves all rows from the model's table, optionally limited
        to a specified number of records.

        Args:
            limit: Maximum number of records to return. If None,
                returns all records. Defaults to None.

        Returns:
            list: All records as class instances, up to the specified
                limit if provided.

        Example:
            >>> # Get all records
            >>> all_trades = TradeRecord.all()
            >>> # Get first 10 records
            >>> recent_trades = TradeRecord.all(limit=10)
        """
        conn = cls.get_connection()
        if limit is None:
            query = f"SELECT * FROM {cls._table}"
        else:
            query = f"SELECT * FROM {cls._table} LIMIT {limit}"
        res = conn.execute(query).fetchall()
        conn.close()
        return res

    @classmethod
    def execute_raw(cls, sql: str, params: tuple | list | dict = None, *, allow_write: bool = False):
        """Execute a validated raw SQL query with parameterized values.

        This method provides safe execution of raw SQL queries by:
        1. Validating the SQL statement type (SELECT only by default)
        2. Checking for dangerous SQL patterns
        3. Using parameterized queries to prevent SQL injection

        Args:
            sql: The SQL query string with placeholders (? or :name).
                 Use '?' for positional parameters with tuple/list params.
                 Use ':name' for named parameters with dict params.
            params: Query parameters as tuple, list, or dict. Defaults to None.
            allow_write: If True, allows INSERT/UPDATE/DELETE operations.
                        Defaults to False for safety.

        Returns:
            list: Query results as class instances for SELECT queries.
            int: Number of affected rows for write operations.

        Raises:
            ValueError: If the SQL contains dangerous patterns or invalid syntax.
            PermissionError: If write operations are attempted without allow_write=True.

        Example:
            Safe parameterized SELECT::

                results = MyModel.execute_raw(
                    "SELECT * FROM mytable WHERE symbol = ? AND volume > ?",
                    ("EURUSD", 0.1)
                )

            Named parameters::

                results = MyModel.execute_raw(
                    "SELECT * FROM mytable WHERE symbol = :sym",
                    {"sym": "EURUSD"}
                )

            Write operations (requires allow_write=True)::

                affected = MyModel.execute_raw(
                    "UPDATE mytable SET closed = ? WHERE order_id = ?",
                    (True, 12345),
                    allow_write=True
                )
        """
        if not sql or not isinstance(sql, str):
            raise ValueError("SQL query must be a non-empty string")

        # Normalize whitespace and convert to uppercase for validation
        sql_normalized = " ".join(sql.split()).upper()

        # Dangerous patterns that should never be allowed
        dangerous_patterns = [
            r";\s*DROP\s+",
            r";\s*DELETE\s+",
            r";\s*TRUNCATE\s+",
            r";\s*ALTER\s+",  
            r";\s*CREATE\s+",
            r"--",  # SQL comments
            r"/\*",  # Block comment
            r"EXEC\s*\(",
            r"EXECUTE\s*\(",
            r"XP_",  # Extended stored procedures
            r"SP_",  # System stored procedures
            r"0x[0-9A-F]+",  # Hex literals often used in attacks
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, sql_normalized, re.IGNORECASE):
                raise ValueError(f"SQL query contains dangerous pattern: {pattern}")

        # Check for multiple statements (multiple semicolons)
        # Allow trailing semicolon but not multiple statements
        sql_stripped = sql.strip().rstrip(";")
        if ";" in sql_stripped:
            raise ValueError("Multiple SQL statements are not allowed")

        # Determine the statement type
        sql_type = sql_normalized.split()[0] if sql_normalized.split() else ""

        # Define allowed statement types
        read_statements = {"SELECT"}
        write_statements = {"INSERT", "UPDATE", "DELETE"}

        if sql_type in write_statements:
            if not allow_write:
                raise PermissionError(
                    f"{sql_type} operations require allow_write=True. "
                    "This is a safety measure to prevent accidental data modification."
                )
        elif sql_type not in read_statements:
            raise ValueError(
                f"Unsupported SQL statement type: {sql_type}. "
                f"Allowed: SELECT, or INSERT/UPDATE/DELETE with allow_write=True"
            )

        # Validate params type
        if params is not None and not isinstance(params, (tuple, list, dict)):
            raise ValueError("params must be tuple, list, or dict")

        # Execute the query with parameterized values
        conn = cls.get_connection()
        try:
            if params:
                cursor = conn.execute(sql, params)
            else:
                cursor = conn.execute(sql)

            if sql_type == "SELECT":
                results = cursor.fetchall()
                conn.close()
                return results
            else:
                # For write operations, commit and return affected row count
                affected_rows = cursor.rowcount
                conn.commit()
                conn.close()
                return affected_rows

        except sqlite3.Error as e:
            conn.close()
            logger.error("SQL execution error: %s", e)
            raise ValueError(f"SQL execution failed: {e}") from e

    @classmethod
    def filter_dict(cls, data: dict, exclude: set[str] = None, include: set[str] = None) -> dict:
        exclude, include = exclude or set(), include or set(cls.fields())
        filter_ = include.difference(exclude)
        return {key: value for key, value in data.items() if key in filter_ and value is not None}