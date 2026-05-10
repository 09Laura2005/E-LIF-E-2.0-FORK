from elife_app.data_access.db import Database
from elife_app.domain.models import DailyEntry
import pytest
from datetime import date
from sqlmodel import Session, SQLModel
import sys
from pathlib import Path

# Add workspace root to path so absolute imports work
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture(scope="function")
def database():
    db = Database("sqlite:///:memory:")
    SQLModel.metadata.create_all(db.engine)
    yield db
    SQLModel.metadata.drop_all(db.engine)


@pytest.fixture(scope="function")
def db(database):
    with Session(database.engine) as session:
        yield session


@pytest.fixture
def seeded_db(db):
    entries = [
        DailyEntry(
            date=date(2025, 1, 1),
            sleep_quality=8,
            stress=3,
            friends=1,
            water_intake=2.5,
            exercise=1,
            mood=7,
            work_hours=8.0,
            hobbies=1,
            steps=8000,
            meds=1,
            period=0,
            score=75
        ),
        DailyEntry(
            date=date(2025, 1, 2),
            sleep_quality=7,
            stress=5,
            friends=0,
            water_intake=2.0,
            exercise=0,
            mood=6,
            work_hours=9.0,
            hobbies=0,
            steps=5000,
            meds=1,
            period=0,
            score=65
        ),
    ]
    db.add_all(entries)
    db.commit()
    for entry in entries:
        db.refresh(entry)
    return db


@pytest.fixture
def sample_items():
    # Sample scores corresponding to the seeded entries for testing purposes.
    return [75, 65]
