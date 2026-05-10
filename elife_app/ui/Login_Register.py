from nicegui import ui, app
from elife_app.domain.models import User


def create_login_page(user_dao) -> None:
    @ui.page('/')
    def login_page() -> None:
        with ui.column().classes('w-full h-screen items-center justify-center gap-4'):
            with ui.card().classes('w-96 p-6 shadow-lg'):
                ui.label('Login').classes('text-2xl font-bold text-center')

                username_input = ui.input('Username').classes('w-full')
                password_input = ui.input(
                    'Password', password=True).classes('w-full')

                def login() -> None:
                    username = username_input.value
                    password = password_input.value

                    user = user_dao.login_user(username, password)

                    if user:
                        app.storage.user['username'] = username
                        ui.navigate.to('/dashboard')
                    else:
                        ui.notify('Wrong username or password',
                                  color='negative')

                ui.button('Login', on_click=login).classes('w-full')
                ui.button('Register', on_click=lambda: ui.navigate.to(
                    '/register')).classes('w-full')

    @ui.page('/register')
    def register_page() -> None:
        with ui.column().classes('w-full h-screen items-center justify-center gap-4'):
            with ui.card().classes('w-96 p-6 shadow-lg'):
                ui.label('Register').classes('text-2xl font-bold text-center')

                username_input = ui.input('Username').classes('w-full')
                password_input = ui.input(
                    'Password', password=True).classes('w-full')
                gender_input = ui.select(
                    ['male', 'female'], label='Gender').classes('w-full')

                def register() -> None:
                    username = username_input.value
                    password = password_input.value
                    gender = gender_input.value

                    if not username or not password or gender not in ('male', 'female'):
                        ui.notify('Please fill all fields correctly',
                                  color='negative')
                        return

                    user = User(username=username,
                                password=password, gender=gender)
                    try:
                        user_dao.register_user(user)
                    except Exception as e:
                        ui.notify(
                            f'Error creating user: {e}', color='negative')
                        return

                    ui.notify('Account created!', color='positive')
                    ui.navigate.to('/')

                ui.button('Create account',
                          on_click=register).classes('w-full')
                ui.button('Back to login', on_click=lambda: ui.navigate.to(
                    '/')).classes('w-full')
