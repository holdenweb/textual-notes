from __future__ import annotations

from textual.app import App

from .db import DB
from .project_list_screen import ProjectListScreen
from .styles import FORM_INPUT_CSS


class ConsoleApp(App):
    """Drill-down note-taking application.

    Pushes ProjectListScreen on mount.  From there the user can
    drill into individual projects and their notes.
    """

    TITLE = "Project Notes"
    CSS = FORM_INPUT_CSS

    def __init__(self, db_name="project_notes"):
        super().__init__()
        self.db = DB(db_name)

    def on_mount(self) -> None:
        self.push_screen(ProjectListScreen(self.db))


def main():
    app = ConsoleApp("project_notes")
    app.run()


if __name__ == "__main__":
    main()
