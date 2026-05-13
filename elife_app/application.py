from __future__ import annotations

from typing import Optional
import socket
import sys

from nicegui import ui

from .data_access.db import Database
from .data_access.dao import EntryDAO, WellnessDAO
from .services.wellness_service import WellnessService
from .ui.Login_Register import create_login_page
from .ui.Dashboard import create_dashboard_page
from .ui.Daily_Report import create_daily_report_page


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
        create_daily_report_page(self.database)

    def run(self, host: str = "0.0.0.0", port: int = 8080, reload: bool = False) -> None:
        """Run the NiceGUI application."""
        def _find_free_port() -> int:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host if host else "", 0))
                return s.getsockname()[1]

        def _port_is_free(p: int) -> bool:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((host if host else "", p))
                    return True
                except OSError:
                    return False

        use_port = port if _port_is_free(port) else _find_free_port()
        if use_port != port:
            print(f"Port {port} in use, starting on free port {use_port}")

        # Call ui.run only once to avoid 'Cannot add middleware after started'.
        ui.run(host=host, port=use_port, reload=reload,
               storage_secret="elife_secret")
