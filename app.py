# app.py: main application logic

from textual.app import App, ComposeResult
from textual.containers import Vertical

from db import DB
from ui import NoteForm


class NoteApp(App):
    DEFAULT_CSS = """
#main-window {
    align: center middle;
}
"""

    def __init__(self, db, *args, **kwargs):
        self.db = db
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        with Vertical(id="main-window"):
            yield NoteForm(self.db)


def main():
    db = DB("project_notes")
    app = NoteApp(db)
    app.run()


if __name__ == "__main__":
    main()
