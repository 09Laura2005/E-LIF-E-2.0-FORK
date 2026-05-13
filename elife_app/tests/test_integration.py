from datetime import date

from elife_app.data_access.dao import EntryDAO, UserDAO, WellnessDAO
from elife_app.domain.models import DailyEntry, User
from elife_app.services.wellness_service import WellnessService


# ============================================================================
# IMPORTANT: How to Run These Tests
# =========================================================================
# DO NOT run this file directly with Python, otherwise it will fail.
# This file uses pytest fixtures that only work through the pytest runner.
#
# Run from project root terminal:
#   pytest elife_app/tests/test_integration.py -v
#
# ============================================================================


def test_create_single_entry_calculates_wellness_score(database, db):
    """Test that a single daily entry can be created and wellness score is calculated."""
    entry_dao = EntryDAO(database.engine)
    wellness_service = WellnessService()

    entry = DailyEntry(
        date=date(2025, 1, 15),
        sleep_quality=8,
        stress=3,
        friends=1,
        water_intake=2.5,
        exercise=1,
        mood=8,
        work_hours=8.0,
        hobbies=1,
        steps=9000,
        meds=1,
        period=0,
    )

    created_entry = entry_dao.create(entry)
    score, advice = wellness_service.calculate_score(created_entry)

    assert created_entry is not None
    assert created_entry.id is not None
    assert score > 0
    assert created_entry.score == score
    assert len(advice) == 0  # All healthy metrics, no advice needed


def test_create_multiple_entries_generates_weekly_report(database, db):
    """Test that multiple entries can be created and weekly report is generated."""
    entry_dao = EntryDAO(database.engine)
    wellness_service = WellnessService()

    entries_data = [
        DailyEntry(date=date(2025, 1, 8), sleep_quality=7, stress=4, friends=1, water_intake=2.0,
                   exercise=1, mood=7, work_hours=8.0, hobbies=1, steps=8000, meds=1, period=0),
        DailyEntry(date=date(2025, 1, 9), sleep_quality=8, stress=3, friends=1, water_intake=2.5,
                   exercise=1, mood=8, work_hours=8.0, hobbies=1, steps=9000, meds=1, period=0),
        DailyEntry(date=date(2025, 1, 10), sleep_quality=6, stress=6, friends=0, water_intake=1.5,
                   exercise=0, mood=6, work_hours=9.0, hobbies=0, steps=5000, meds=1, period=0),
        DailyEntry(date=date(2025, 1, 11), sleep_quality=9, stress=2, friends=1, water_intake=3.0,
                   exercise=1, mood=9, work_hours=7.0, hobbies=1, steps=10000, meds=1, period=0),
        DailyEntry(date=date(2025, 1, 12), sleep_quality=7, stress=5, friends=1, water_intake=2.0,
                   exercise=1, mood=7, work_hours=8.0, hobbies=1, steps=8500, meds=1, period=0),
        DailyEntry(date=date(2025, 1, 13), sleep_quality=8, stress=4, friends=0, water_intake=2.5,
                   exercise=1, mood=8, work_hours=8.0, hobbies=1, steps=9500, meds=1, period=0),
        DailyEntry(date=date(2025, 1, 14), sleep_quality=7, stress=3, friends=1, water_intake=2.0,
                   exercise=1, mood=8, work_hours=8.0, hobbies=1, steps=8000, meds=1, period=0),
    ]

    created_entries = [entry_dao.create(e) for e in entries_data]

    for entry in created_entries:
        wellness_service.calculate_score(entry)

    weekly_report = wellness_service.weekly_report(created_entries)

    assert len(created_entries) == 7
    assert all(e.id is not None for e in created_entries)
    assert "Weekly Average Score" in weekly_report
    assert float(weekly_report.split(": ")[1]) > 0


def test_user_registration_login_and_entry_creation(database, db):
    """Test complete flow: user registration, login, and wellness entry creation."""
    wellness_dao = WellnessDAO(database.engine)
    wellness_service = WellnessService()

    # Register new user
    user = User(username="testuser", password="password123", gender="female")
    registered_user = wellness_dao.register_user(user)

    assert registered_user is not None
    assert registered_user.id is not None
    assert registered_user.username == "testuser"

    # Login user
    logged_in_user = wellness_dao.login_user("testuser", "password123")
    assert logged_in_user is not None
    assert logged_in_user.id == registered_user.id

    # Create wellness entry
    entry = DailyEntry(
        date=date(2025, 1, 20),
        sleep_quality=9,
        stress=2,
        friends=1,
        water_intake=3.0,
        exercise=1,
        mood=9,
        work_hours=7.0,
        hobbies=1,
        steps=11000,
        meds=1,
        period=0,
    )

    created_entry = wellness_dao.add_entry(entry)
    score, advice = wellness_service.calculate_score(created_entry)

    assert created_entry is not None
    assert created_entry.id is not None
    assert score > 60  # Healthy lifestyle should have high score
    assert len(advice) == 0  # All metrics are healthy
