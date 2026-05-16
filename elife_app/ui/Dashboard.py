from nicegui import ui, app
from datetime import date
from elife_app.domain.models import DailyEntry
from elife_app.services.wellness_service import WellnessService


def create_dashboard_page(entry_dao, wellness_service: WellnessService) -> None:
    @ui.page('/dashboard')
    def dashboard_page() -> None:
        user_id = app.storage.user.get('user_id')
        username = app.storage.user.get('username')

        if not user_id or not username:
            ui.navigate.to('/')
            return

        def logout() -> None:
            app.storage.user.clear()
            ui.navigate.to('/')

        ui.add_head_html('''
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Source+Sans+3:wght@400;500;600&display=swap" rel="stylesheet">
            <style>
                :root {
                    --bg-start: #0f172a;
                    --bg-end: #1f2937;
                    --card: rgba(255, 255, 255, 0.08);
                    --card-border: rgba(255, 255, 255, 0.18);
                    --accent: #f59e0b;
                    --text: #f8fafc;
                    --muted: #cbd5f5;
                }
                body {
                    font-family: 'Source Sans 3', sans-serif;
                    background: radial-gradient(1200px 600px at 10% -10%, #1e3a8a33, transparent),
                                radial-gradient(1200px 700px at 90% 0%, #f59e0b22, transparent),
                                linear-gradient(120deg, var(--bg-start), var(--bg-end));
                    color: var(--text);
                }
                .dashboard-title {
                    font-family: 'Space Grotesk', sans-serif;
                    letter-spacing: 0.3px;
                }
                .glass-card {
                    background: var(--card);
                    border: 1px solid var(--card-border);
                    backdrop-filter: blur(10px);
                    border-radius: 18px;
                }
                .pill-button .q-btn {
                    border-radius: 999px;
                }
                .muted-text { color: var(--muted); }
            </style>
        ''')

        with ui.column().classes('w-full items-center gap-6 p-6 md:p-10'):
            with ui.row().classes('w-full max-w-6xl items-center justify-between gap-4'):
                with ui.column().classes('gap-2'):
                    ui.label(f'Welcome back, {username}!').classes(
                        'dashboard-title text-3xl md:text-4xl font-bold')
                    ui.label('Pick an action below or start a new check-in.').classes(
                        'muted-text')
                ui.button('Logout', on_click=logout).classes(
                    'pill-button bg-slate-900/70 text-white')

            with ui.row().classes('w-full max-w-6xl gap-4 md:gap-6'):
                with ui.card().classes('glass-card w-full md:w-1/3 p-5 gap-3'):
                    ui.label('Manage Entries').classes('text-xl font-semibold')
                    ui.label(
                        'Edit, delete, or review previous check-ins.').classes('muted-text')
                    ui.button('Open entries', on_click=lambda: ui.navigate.to('/daily-entry')).classes(
                        'pill-button bg-amber-400 text-slate-900')

                with ui.card().classes('glass-card w-full md:w-1/3 p-5 gap-3'):
                    ui.label('Daily Report').classes('text-xl font-semibold')
                    ui.label('See today\'s score and recommendations.').classes(
                        'muted-text')
                    ui.button('View report', on_click=lambda: ui.navigate.to('/daily-report')).classes(
                        'pill-button bg-slate-900/70 text-white')

                with ui.card().classes('glass-card w-full md:w-1/3 p-5 gap-3'):
                    ui.label('Monthly Report').classes('text-xl font-semibold')
                    ui.label('Review the last 28 days at a glance.').classes(
                        'muted-text')
                    ui.button('View monthly', on_click=lambda: ui.navigate.to('/monthly-report')).classes(
                        'pill-button bg-slate-900/70 text-white')

            with ui.card().classes('glass-card w-full max-w-6xl p-6'):
                with ui.expansion('Start daily check-in', icon='edit_note').classes('w-full'):
                    with ui.column().classes('gap-4'):
                        sleep = ui.slider(min=0, max=10, value=5).props(
                            'label-always')
                        ui.label('Sleep quality (0-10)')

                        stress = ui.slider(
                            min=0, max=10, value=5).props('label-always')
                        ui.label('Stress (0-10)')

                        mood = ui.slider(min=0, max=10, value=5).props(
                            'label-always')
                        ui.label('Mood (0-10)')

                        with ui.row().classes('w-full gap-4'):
                            water = ui.number(label='Water intake (litres)',
                                              min=0, max=5, value=1.5).classes('w-full')
                            steps = ui.number(label='Step count', min=0,
                                              max=50000, value=0).classes('w-full')
                            work_hours = ui.number(label='Work hours', min=0,
                                                   max=16, value=8).classes('w-full')

                        with ui.row().classes('w-full gap-4 flex-wrap'):
                            friends = ui.checkbox('Did you see friends today?')
                            exercise = ui.checkbox('Did you exercise today?')
                            hobbies = ui.checkbox('Did you do a hobby today?')
                            meds = ui.checkbox('Did you take your meds today?')
                            period = ui.checkbox('Are you on your period?')

                        result_label = ui.label('')

                        def submit():
                            entry = DailyEntry(
                                user_id=int(user_id),
                                date=date.today(),
                                sleep_quality=int(sleep.value),
                                stress=int(stress.value),
                                mood=int(mood.value),
                                water_intake=float(water.value),
                                steps=int(steps.value),
                                work_hours=float(work_hours.value),
                                friends=int(friends.value),
                                exercise=int(exercise.value),
                                hobbies=int(hobbies.value),
                                meds=int(meds.value),
                                period=int(period.value),
                            )
                            score, advice = wellness_service.calculate_score(
                                entry)
                            entry.score = score
                            created_entry = entry_dao.create(entry)
                            stamp = (
                                created_entry.created_at.strftime(
                                    '%Y-%m-%d %H:%M')
                                if created_entry.created_at
                                else 'unknown'
                            )
                            result_label.text = (
                                f'Your wellness score: {score}\n'
                                f'Logged at: {stamp}\n'
                                + '\n'.join(advice)
                            )

                        ui.button('Submit check-in', on_click=submit).classes(
                            'pill-button bg-amber-400 text-slate-900')
