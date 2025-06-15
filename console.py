from textual.app import App
from note_screen import note_screen


class ConsoleApp(App):
    """
    This app has the responsibility of presenting the basic user interface
    and responding to user function selection.

    In the initial version, each function is selected by its"""

    SCREENS = {"note": note_screen("project_notes")}
    BINDINGS = [("b", "notify(str(push_screen('note')))", "NOTE")]


if __name__ == "__main__":
    app = ConsoleApp()
    app.run()
