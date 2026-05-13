from elife_app.domain.models import User, DailyEntry
import pytest
from datetime import date
from sqlmodel import select
import sys
from pathlib import Path

# Add workspace root to path so absolute imports work
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
# IMPORTANT: How to Run These Tests
# =========================================================================
# DO NOT run this file directly with Python, otherwise it will fail.
# This file uses pytest fixtures that only work through the pytest runner.
#
# Run from project root terminal:
#   pytest -v elife_app/tests/test_db.py
#
# ============================================================================

# ==================== TEST 1: Query Seeded Daily Entries ====================


def test_query_seeded_daily_entries(seeded_db):
    """
    Test that seeded database entries can be queried and verified.

    This test verifies that the fixture correctly creates sample DailyEntry
    records and that they can be retrieved from the database.
    """
    # Query all daily entries from seeded database
    entries = seeded_db.exec(select(DailyEntry)).all()

    # Verify correct number of seeded entries
    assert len(entries) == 2, "Should have 2 seeded entries"

    # Verify first entry properties
    assert entries[0].date == date(2025, 1, 1), "First entry date should match"
    assert entries[0].sleep_quality == 8, "First entry sleep quality should be 8"
    assert entries[0].mood == 7, "First entry mood should be 7"

    # Verify second entry properties
    assert entries[1].date == date(
        2025, 1, 2), "Second entry date should match"
    assert entries[1].sleep_quality == 7, "Second entry sleep quality should be 7"


# ==================== TEST 2: Create and Persist User ====================
def test_create_and_persist_user(db):
    """
    Test that a new User can be created and persisted to the database.

    This test verifies the database layer correctly saves user information
    and that the data can be retrieved with the correct values.
    """
    # Create a new user
    user = User(
        username="alice@example.com",
        password="securepassword123",
        gender="female"
    )

    # Add and save to database
    db.add(user)
    db.commit()
    db.refresh(user)

    # Verify user was assigned an ID
    assert user.id is not None, "User should have an ID after commit"
    assert user.id > 0, "User ID should be positive"

    # Query the user back from database
    query_user = db.exec(
        select(User).where(User.username == "alice@example.com")
    ).first()

    # Verify retrieved user matches saved data
    assert query_user is not None, "User should be retrievable from database"
    assert query_user.username == "alice@example.com", "Username should match"
    assert query_user.gender == "female", "Gender should match"


# ==================== TEST 3: Save DailyEntry and Retrieve by Date ====================
def test_save_daily_entry_and_retrieve_by_date(db):
    """
    Test that a new DailyEntry can be saved and retrieved by specific date.

    This test verifies that the database can store wellness data and that
    entries can be queried by date for user history lookups.
    """
    # Create a new daily entry
    entry = DailyEntry(
        date=date(2025, 2, 15),
        sleep_quality=9,
        stress=2,
        friends=1,
        water_intake=4.0,
        exercise=1,
        mood=8,
        work_hours=8.0,
        hobbies=1,
        steps=10000,
        meds=1,
        period=0,
        score=75
    )

    # Save to database
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Verify entry was assigned an ID
    assert entry.id is not None, "Entry should have an ID after commit"

    # Query entry by date
    retrieved_entry = db.exec(
        select(DailyEntry).where(DailyEntry.date == date(2025, 2, 15))
    ).first()

    # Verify retrieved entry matches saved data
    assert retrieved_entry is not None, "Entry should be retrievable by date"
    assert retrieved_entry.sleep_quality == 9, "Sleep quality should match"
    assert retrieved_entry.stress == 2, "Stress level should match"
    assert retrieved_entry.score == 75, "Score should match"
    assert retrieved_entry.steps == 10000, "Steps should match"
