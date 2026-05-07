from nicegui import ui, app


def create_dashboard_page() -> None:
    @ui.page('/dashboard')
    def dashboard_page() -> None:
        username = app.storage.user.get('username')

        if not username:
            ui.navigate.to('/')
            return

        def logout() -> None:
            app.storage.user.clear()
            ui.navigate.to('/')

        with ui.column().classes('w-full h-screen items-center justify-center gap-4'):
            ui.label(f'Welcome, {username}!').classes('text-2xl font-bold')
            ui.button('Logout', on_click=logout)