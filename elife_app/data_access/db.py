from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, Session, create_engine

from elife_app.domain.models import DailyEntry


class Database:
    """Database facade (engine + schema init + session scope)."""

    def __init__(self, database_url: Optional[str] = None, *, echo: bool = False) -> None:
        self._database_url = database_url or os.getenv(
            "DATABASE_URL") or self._default_sqlite_url()
        self._engine: Engine = create_engine(
            self._database_url, echo=echo, connect_args={
                "check_same_thread": False}
        )

    @staticmethod
    def _default_sqlite_url() -> str:
        Path("data").mkdir(parents=True, exist_ok=True)
        return "sqlite:///data/elife.db"

    @property
    def engine(self) -> Engine:
        return self._engine

    def init_schema(self) -> None:
        """Create tables if they don't exist yet."""
        SQLModel.metadata.create_all(self._engine)

    @contextmanager
    def session_scope(self) -> Iterator[Session]:
        """Provide a transactional scope around a series of operations."""
        session = Session(self._engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


def create_db(database_url: Optional[str] = None, *, echo: bool = False) -> Database:
    """Convenience wrapper used by the application to ensure the schema exists.

    Returns the created `Database` instance.
    """
    db = Database(database_url, echo=echo)
    db.init_schema()
    return db
