from textual.app import App

from .api import SolApi
from .screens import Dashboard, LoginScreen


class SolApp(App):
    CSS = "Screen { background: $surface; }"
    BINDINGS = [("q", "quit", "Ukončit")]

    def __init__(self):
        super().__init__()
        self.api = SolApi()

    def on_mount(self):
        self.push_screen(LoginScreen(self.api))

    def switch_to_dashboard(self):
        self.push_screen(Dashboard(self.api))
