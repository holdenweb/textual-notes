from textual.app import App
from note_screen import build_note_screen
from forms.project import build_project_screen


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
        ("b", "push_screen('note')", "NOTE"),
        ("p", "push_screen('project')", "PROJECT"),
    ]


if __name__ == "__main__":
    app = ConsoleApp()
    app.run()
