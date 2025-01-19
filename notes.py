import argparse

from textual.app import App
from textual.app import ComposeResult
from textual.containers import Center
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.widgets import Button
from textual.widgets import Label
from textual.widgets import Placeholder
from textual.widgets import Select

import db


class NoteForm(Vertical):
    DEFAULT_CSS = """
"""

    def __init__(self, db, otyp=None, *args, **kwargs):
        self.db = db
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        self.btn: Button = Button("Submit")
        with Vertical():
            yield Horizontal(
                Select([], id="otyp-sel"), Placeholder(id="inst-sel"), id="selections"
            )
            with Horizontal(id="status"):
                if not self.app.otyp:
                    yield Splash()
                else:
                    yield NoteEditor()


class NoteEditor(Horizontal):
    def compose(self) -> ComposeResult:
        yield Vertical(
            Placeholder(id="content"),
            Center(Button("submit"), id="buttonbar"),
            id="info",
        )
        yield Placeholder(id="operations")


class Splash(Center):
    def compose(self):
        yield Label("Select an object type to edit")


class NoteApp(App):
    CSS_PATH = "x.tcss"

    def __init__(self, otyp, *args, **kwargs):
        self.db = db.DB("project_notes")  # This could become a CLI option
        self.otyp = otyp
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield NoteForm(self.db, otyp=self.otyp, id="main-window")

    def on_click(self, event):
        self.log(self.tree)
        self.log(self.css_tree)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--type", default=None, help="The object type to be maintained."
    )
    args = parser.parse_args()
    print(args)
    app = NoteApp(otyp=args.type)
    app.run()


if __name__ == "__main__":
    main()
