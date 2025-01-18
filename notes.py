from textual.app import App
from textual.app import ComposeResult
from textual.containers import Center, Horizontal
from textual.containers import Vertical
from textual.widgets import Button, Placeholder

import db


class NoteForm(Vertical):
    DEFAULT_CSS = """
"""

    def __init__(self, db, *args, **kwargs):
        self.db = db
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        self.btn: Button = Button("Submit")
        with Vertical():
            yield Horizontal(
                Placeholder(id="otyp-sel"), Placeholder(id="inst-sel"), id="selections"
            )
            yield Horizontal(Placeholder(), Placeholder(), id="status")
            yield Center(self.btn, id="buttonbar")


class NoteApp(App):
    CSS_PATH = "x.tcss"

    def compose(self) -> ComposeResult:
        self.db = db.DB("project_notes")
        yield NoteForm(self, id="main-window")

    def on_click(self, event):
        self.log(self.tree)
        self.log(self.css_tree)


def main():
    app = NoteApp()
    app.run()


if __name__ == "__main__":
    main()
