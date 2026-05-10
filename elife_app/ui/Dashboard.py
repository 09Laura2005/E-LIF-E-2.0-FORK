from nicegui import ui, app
from datetime import date
from elife_app.domain.models import DailyEntry
from elife_app.services.wellness_service import WellnessService


def create_dashboard_page(entry_dao, wellness_service: WellnessService) -> None:
    @ui.page('/dashboard')
    def dashboard_page() -> None:
        username = app.storage.user.get('username')

        if not username:
            ui.navigate.to('/')
            return

        def logout() -> None:
            app.storage.user.clear()
            ui.navigate.to('/')

        with ui.column().classes('w-full items-center gap-4 p-8'):
            ui.label(f'Welcome, {username}!').classes('text-2xl font-bold')

            ui.label('Daily Check-in').classes('text-xl font-semibold')

            sleep = ui.slider(min=0, max=10, value=5).props('label-always')
            ui.label('Sleep quality (0-10)')

            stress = ui.slider(min=0, max=10, value=5).props('label-always')
            ui.label('Stress (0-10)')

            mood = ui.slider(min=0, max=10, value=5).props('label-always')
            ui.label('Mood (0-10)')

            water = ui.number(label='Water intake (litres)', min=0, max=5, value=1.5)
            steps = ui.number(label='Step count', min=0, max=50000, value=0)
            work_hours = ui.number(label='Work hours', min=0, max=16, value=8)

            friends = ui.checkbox('Did you see friends today?')
            exercise = ui.checkbox('Did you exercise today?')
            hobbies = ui.checkbox('Did you do a hobby today?')
            meds = ui.checkbox('Did you take your meds today?')
            period = ui.checkbox('Are you on your period?')

            result_label = ui.label('')

            def submit():
                entry = DailyEntry(
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
                score, advice = wellness_service.calculate_score(entry)
                entry_dao.create(entry)
                result_label.text = f'Your wellness score: {score}\n' + '\n'.join(advice)

            ui.button('Submit', on_click=submit)
            ui.button('Logout', on_click=logout).classes('mt-4')