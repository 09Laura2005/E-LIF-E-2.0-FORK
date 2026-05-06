from __future__ import annotations
from sqlmodel import Session
from elife_app.domain.models import DailyEntry

import sys
from pathlib import Path
from datetime import date, timedelta

# MUST be before importing from elife_app
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class WellnessSeeder:
    """Seeds the database with sample wellness tracking data."""

    def seed(self, session: Session, days: int = 7) -> None:
        """
        Insert sample daily wellness entries for the past N days.

        """
        entries = []
        today = date.today()

        for i in range(days):
            current_date = today - timedelta(days=i)
            entry = DailyEntry(
                date=current_date,
                sleep_quality=(i % 11),  # 0-10
                stress=(i % 11),  # 0-10
                friends=i % 2,  # 0-1
                water_intake=float((i % 6)),  # 0-5
                exercise=i % 2,  # 0-1
                mood=(i % 11),  # 0-10
                work_hours=float((i % 17)),  # 0-16
                hobbies=i % 2,  # 0-1
                steps=(i % 50001),  # 0-50000
                meds=i % 2,  # 0-1
                period=i % 2,  # 0-1
            )
            entries.append(entry)

        for entry in entries:
            session.add(entry)
