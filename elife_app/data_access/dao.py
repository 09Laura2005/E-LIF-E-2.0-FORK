
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from ..domain.models import DailyEntry, User


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