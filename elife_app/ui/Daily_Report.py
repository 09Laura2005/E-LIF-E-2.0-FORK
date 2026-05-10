from elife_app.services.wellness_service import WellnessService
from elife_app.domain.models import DailyEntry
from elife_app.data_access.db import Database
from datetime import date

import sys
from pathlib import Path

from nicegui import ui
from sqlmodel import select

# make package import work when file is executed directly
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def create_daily_report_page() -> None:
    @ui.page('/daily-report')
    def daily_report_page() -> None:
        db = Database()
        db.init_schema()
        wellness = WellnessService()

        entries_container = ui.column().classes('w-full gap-2')
        avg_label = ui.label('')

        def load_entries():
            with db.session_scope() as session:
                stmt = select(DailyEntry).order_by(DailyEntry.date.desc())
                return session.exec(stmt).all()

        def refresh() -> None:
            entries = load_entries()
            entries_container.clear()

            for entry in entries:
                create_entry_row(entry)

            if entries:
                avg = sum(e.score for e in entries) / len(entries)
                avg_label.set_text(f'Average score: {avg:.1f}')
            else:
                avg_label.set_text('No data.')

        def create_entry_row(entry: DailyEntry) -> None:
            def open_edit() -> None:
                with ui.dialog().classes('w-1/2') as dlg:
                    ui.label('Edit entry').classes('text-lg font-medium')
                    d_input = ui.input(
                        label='Date', value=entry.date.isoformat())
                    sleep_input = ui.number(
                        label='Sleep quality', value=entry.sleep_quality)
                    stress_input = ui.number(
                        label='Stress', value=entry.stress)
                    mood_input = ui.number(label='Mood', value=entry.mood)
                    steps_input = ui.number(label='Steps', value=entry.steps)
                    work_input = ui.number(
                        label='Work hours', value=entry.work_hours)

                    def save_edit() -> None:
                        d = date.fromisoformat(d_input.value)
                        with db.session_scope() as session:
                            obj = session.get(DailyEntry, entry.id)
                            obj.date = d
                            obj.sleep_quality = int(sleep_input.value)
                            obj.stress = int(stress_input.value)
                            obj.mood = int(mood_input.value)
                            obj.steps = int(steps_input.value)
                            obj.work_hours = float(work_input.value)
                            score, _ = wellness.calculate_score(obj)
                            obj.score = score
                            session.add(obj)

                        dlg.close()
                        refresh()

                    ui.button('Save', on_click=save_edit)
                    ui.button('Cancel', on_click=dlg.close)
                dlg.open()

            def delete_entry() -> None:
                with db.session_scope() as session:
                    obj = session.get(DailyEntry, entry.id)
                    if obj:
                        session.delete(obj)

                refresh()

            with ui.row().classes('items-center justify-between w-full py-2 px-4 border rounded'):
                ui.label(f'{entry.date.isoformat()} — score: {entry.score}')
                with ui.row():
                    ui.button('Edit', on_click=open_edit)
                    ui.button('Delete', on_click=delete_entry)

        # Add new entry form
        with ui.card().classes('w-full'):
            ui.label('Add new daily entry').classes('text-lg font-medium')
            date_input = ui.input(label='Date', placeholder='YYYY-MM-DD')
            sleep_input = ui.number(label='Sleep quality', value=5)
            stress_input = ui.number(label='Stress', value=5)
            mood_input = ui.number(label='Mood', value=5)
            steps_input = ui.number(label='Steps', value=0)
            work_input = ui.number(label='Work hours', value=0.0)

            def add_entry() -> None:
                try:
                    d = date.fromisoformat(date_input.value)
                except Exception:
                    ui.notify(
                        'Invalid date format, use YYYY-MM-DD', color='red')
                    return

                entry = DailyEntry(
                    date=d,
                    sleep_quality=int(sleep_input.value),
                    stress=int(stress_input.value),
                    friends=0,
                    water_intake=0.0,
                    exercise=0,
                    mood=int(mood_input.value),
                    work_hours=float(work_input.value),
                    hobbies=0,
                    steps=int(steps_input.value),
                    meds=0,
                    period=0,
                )

                score, _ = wellness.calculate_score(entry)
                entry.score = score

                with db.session_scope() as session:
                    session.add(entry)

                date_input.set_value('')
                refresh()

            ui.button('Add entry', on_click=add_entry)

        ui.separator()
        ui.label('Entries').classes('text-lg font-medium')
        entries_container
        avg_label
        ui.button('Refresh', on_click=refresh)

        refresh()


__all__ = ['create_daily_report_page']
