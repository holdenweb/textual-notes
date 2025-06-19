from textual.app import App
from textual.widgets import Footer, Header
from note_screen import build_note_screen
from project_screen import build_project_screen


class ConsoleApp(App):
    """
    This app has the responsibility of presenting the basic user interface
    and responding to user function selection.

    In the initial version, each function is selected by its"""

    SCREENS = {
        "note": build_note_screen("project_notes"),
        "project": build_project_screen("project_notes"),
    }

    BINDINGS = [
        ("p", "push_screen('project')", "Projects"),
        ("n", "push_screen('note')", "Notes"),
        ("q", "quit()", "Quit"),
    ]

    def compose(self):
        yield Header(show_clock=True, name="textual_forms demo")
        yield Footer()


if __name__ == "__main__":
    app = ConsoleApp()
    app.run()
