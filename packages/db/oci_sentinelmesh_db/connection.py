"""SQLite connection helpers."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = "./data/oci-sentinelmesh.db"
PERSISTENCE_ENABLED_ENV = "OCI_SENTINEL_PERSISTENCE_ENABLED"
DB_PATH_ENV = "OCI_SENTINEL_DB_PATH"


def database_path() -> Path:
    """Return the configured local SQLite database path."""

    return Path(os.getenv(DB_PATH_ENV, DEFAULT_DB_PATH))


def persistence_enabled() -> bool:
    """Return whether API scan persistence is enabled."""

    raw_value = os.getenv(PERSISTENCE_ENABLED_ENV, "true").strip().lower()
    return raw_value in {"1", "true", "yes", "on"}


def connect(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Open a SQLite connection, creating the parent directory if needed."""

    path = Path(db_path) if db_path is not None else database_path()
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection
