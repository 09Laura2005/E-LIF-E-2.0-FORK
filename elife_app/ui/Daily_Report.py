from __future__ import annotations

from datetime import date

from nicegui import app, ui

from elife_app.data_access.dao import EntryDAO
from elife_app.services.wellness_service import WellnessService


def create_daily_report_page(entry_dao: EntryDAO, wellness_service: WellnessService) -> None:
    @ui.page('/daily-report')
    def daily_report_page() -> None:
        user_id = app.storage.user.get('user_id')
        username = app.storage.user.get('username')

        if not user_id or not username:
            ui.navigate.to('/')
            return

        with ui.column().classes('w-full items-center gap-4 p-8'):
            ui.label(f'Daily report for {username}').classes(
                'text-2xl font-bold')
            ui.button('Back to dashboard',
                      on_click=lambda: ui.navigate.to('/dashboard'))

            date_label = ui.label('')
            timestamp_label = ui.label('')
            score_label = ui.label('')
            advice_container = ui.column().classes('w-full gap-2')

            def get_latest_entry():
                entries = entry_dao.list_for_user(int(user_id))
                if not entries:
                    return None, None

                today = date.today()
                for entry in entries:
                    if entry.date == today:
                        return entry, 'today'

                return entries[0], 'latest'

            def refresh() -> None:
                advice_container.clear()

                entry, label = get_latest_entry()
                if entry is None:
                    date_label.set_text(
                        'No entries yet. Add a daily entry first.')
                    timestamp_label.set_text('')
                    score_label.set_text('')
                    return

                score, advice = wellness_service.calculate_score(entry)
                score_label.set_text(f'Wellness score: {score}')

                if label == 'today':
                    date_label.set_text(
                        f'Report for today ({entry.date.isoformat()})')
                else:
                    date_label.set_text(
                        f'Most recent entry ({entry.date.isoformat()})')

                if entry.created_at:
                    stamp = entry.created_at.strftime('%Y-%m-%d %H:%M')
                else:
                    stamp = 'unknown'
                timestamp_label.set_text(f'Logged at: {stamp}')

                if advice:
                    for tip in advice:
                        ui.label(tip)
                else:
                    ui.label('No recommendations for today. Keep it up!')

            ui.button('Refresh', on_click=refresh)
            refresh()


__all__ = ['create_daily_report_page']
