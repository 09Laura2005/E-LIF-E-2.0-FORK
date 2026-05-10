from __future__ import annotations

from typing import Optional

from nicegui import ui

from .data_access.db import Database
from .data_access.dao import EntryDAO, WellnessDAO
from .services.wellness_service import WellnessService
from .ui.Login import create_login_page
from .ui.Dashboard import create_dashboard_page


class ElifeApplication:
    """Application composition root."""

    def __init__(self, database: Optional[Database] = None) -> None:
        self.database = database or Database()
        self.database.init_schema()

        engine = self.database.engine

        self.entry_dao = EntryDAO(engine)
        self.wellness_service = WellnessService()

        self.wellness_dao = WellnessDAO(engine)

        create_login_page(self.wellness_dao)
        create_dashboard_page(self.entry_dao, self.wellness_service)

    def run(self, host: str = "0.0.0.0", port: int = 8080, reload: bool = False) -> None:
        """Run the NiceGUI application."""
        ui.run(host=host, port=port, reload=reload,
               storage_secret="elife_secret")
