
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from elife_app.domain.models import DailyEntry, User


class BaseDAO:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def session(self) -> Session:
        return Session(self.engine)


class EntryDAO(BaseDAO):

    def create(self, entry: DailyEntry) -> DailyEntry:
        with self.session() as session:
            session.add(entry)
            session.commit()
            session.refresh(entry)
            return entry

    def list_all(self) -> List[DailyEntry]:
        with self.session() as session:
            return list(session.exec(select(DailyEntry)).all())

    def list_for_user(self, user_id: int) -> List[DailyEntry]:
        with self.session() as session:
            statement = (
                select(DailyEntry)
                .where(DailyEntry.user_id == user_id)
                .order_by(DailyEntry.date.desc())
            )
            return list(session.exec(statement).all())

    def get_by_id(self, entry_id: int) -> Optional[DailyEntry]:
        with self.session() as session:
            return session.get(DailyEntry, entry_id)


class UserDAO(BaseDAO):

    def create(self, user: User) -> User:
        with self.session() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def get_by_username(self, username: str) -> Optional[User]:
        with self.session() as session:
            return session.exec(select(User).where(User.username == username)).first()


class WellnessDAO:
    """Higher-level DAO used by the CLI app.

    This composes the lower-level DAOs and provides the methods expected
    by `elife_app.main` (register_user, login_user, add_entry, get_user_entries).
    """

    def __init__(self, engine: Engine | None = None) -> None:
        if engine is None:
            from elife_app.data_access.db import Database

            db = Database()
            self.engine = db.engine
        else:
            self.engine = engine

        self.user_dao = UserDAO(self.engine)
        self.entry_dao = EntryDAO(self.engine)

    def register_user(self, user: User) -> User:
        return self.user_dao.create(user)

    def login_user(self, username: str, password: str) -> Optional[User]:
        user = self.user_dao.get_by_username(username)
        if user and user.password == password:
            return user
        return None

    def add_entry(self, entry: DailyEntry) -> DailyEntry:
        return self.entry_dao.create(entry)

    def get_user_entries(self, user_id: int) -> List[DailyEntry]:
        return self.entry_dao.list_for_user(user_id)
