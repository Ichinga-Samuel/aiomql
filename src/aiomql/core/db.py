import os
import sqlite3
import re
from logging import getLogger
from dataclasses import Field, fields, asdict, MISSING, is_dataclass
from typing import ClassVar

from .config import Config

logger = getLogger(__name__)


class DB:
    _table: ClassVar[str] = ""
    TYPES: ClassVar[dict] = {str: "TEXT", float: "REAL", int: "INTEGER", bool: "BOOLEAN", None: "NULL", bytes: "BLOB"}
    config: ClassVar[Config]
    conn: sqlite3.Connection
    cursor: sqlite3.Cursor

    def __new__(cls, *args, **kwargs):
        cls.config = Config()
        return super().__new__(cls)

    def __post_init__(self):
        self.init_db()

    def init_db(self):
        db_name = getattr(self.config, "db_name", os.getenv("DB_NAME", "db.sqlite3"))
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = self.dict_factory()
        self.cursor = self.conn.cursor()
        self.create_table(self.conn)

    @classmethod
    def get_connection(cls):
        db_name = os.getenv("DB_NAME", "db.sqlite3")
        conn = sqlite3.connect(db_name)
        conn.row_factory = cls.dict_factory()
        return conn

    @classmethod
    def create_table(cls, conn: sqlite3.Connection):
        try:
            if not is_dataclass(cls):
                return
            cls._table = cls._table or cls.__name__.lower()
            columns = cls.get_columns()
            q = f"""CREATE TABLE IF NOT EXISTS '{cls._table}' ({columns})"""
            conn.execute(f"""CREATE TABLE IF NOT EXISTS '{cls._table}' ({columns})""")
            conn.commit()
        except Exception as e:
            logger.error("%s: Failed to create table", e)

    @classmethod
    def dict_factory(cls):
        def dict_factory(cursor, row):
            cols = [column[0] for column in cursor.description]
            kw = {key: value for key, value in zip(cols, row)}
            print(type(cls), cls.__name__)
            return cls(**kw)
        return dict_factory

    @staticmethod
    def sanitize(identifier):
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", identifier):
            return f'"{identifier}"'
        raise ValueError("Invalid table name")

    @classmethod
    def types(cls, key):
        return cls.TYPES.get(key, "TEXT")

    @staticmethod
    def get_default(col: Field):
        if not isinstance(col.default, type(MISSING)):
            return f"DEFAULT {col.default}"
        elif not isinstance(col.default_factory, type(MISSING)):
            return f"DEFAULT {col.default_factory()}"
        else:
            return ""

    @staticmethod
    def get_metadata(col: Field):
        return f"{' '.join(meta for meta, value in col.metadata.items() if value)}"

    @classmethod
    def get_columns(cls):
        cols = fields(cls)
        cols = [f"'{col.name}' {cls.types(col.type)} {cls.get_metadata(col)} {cls.get_default(col)}" for col in
                cols]
        return ",".join(cols)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def asdict(self):
        return asdict(self)

    def get_data(self):
        return self.asdict()

    @classmethod
    def clear(cls):
        conn = cls.get_connection()
        conn.execute(f"DELETE FROM {cls._table}")
        conn.commit()
        conn.close()

    def save(self, commit=True):
        data = self.get_data()
        columns = ", ".join(self.sanitize(key) for key in data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = tuple(data.values())
        table = self.sanitize(self._table)
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, values)
        if commit:
            self.commit()

    @classmethod
    def get(cls, **kwargs):
        conn = cls.get_connection()
        _query = " AND ".join([f'"{key}" = "{value}"' for key, value in kwargs.items()])
        query = f"""SELECT * FROM {cls.sanitize(cls._table)} WHERE {_query}"""
        res = conn.execute(query).fetchone()
        conn.close()
        return res

    @classmethod
    def filter(cls, **kwargs):
        conn = cls.get_connection()
        _query = " AND ".join([f'"{key}" = "{value}"' for key, value in kwargs.items()])
        # _query = " AND ".join([f'{key} = {value}' for key, value in kwargs.items()])
        _query = f"WHERE {_query}" if _query else ""
        query = f"SELECT * FROM {cls.sanitize(cls._table)} {_query}"
        res = conn.execute(query).fetchall()
        conn.close()
        return res

    @classmethod
    def update(cls, data=None, /, **kwargs):
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
        fs = fields(cls)
        return [f.name for f in fs]

    @classmethod
    def drop_table(cls):
        conn = cls.get_connection()
        conn.execute(f"DROP TABLE IF EXISTS {cls._table}")
        conn.commit()
        conn.close()
