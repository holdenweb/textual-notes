import argparse

from textual.app import App
from textual.app import ComposeResult
from textual.containers import Center
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.widgets import Button
from textual.widgets import Placeholder

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
            with Horizontal(id="status"):
                yield Vertical(
                    Placeholder(id="content"),
                    Center(Button("submit"), id="buttonbar"),
                    id="info",
                )
                yield Placeholder(id="operations")


class NoteApp(App):
    CSS_PATH = "x.tcss"

    def __init__(self, otyp, *args, **kwargs):
        self.db = db.DB("project_notes")
        self.otyp = otyp
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield NoteForm(self.db, id="main-window")

    def on_click(self, event):
        self.log(self.tree)
        self.log(self.css_tree)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--type", default="notes", help="The object type to be maintained."
    )
    args = parser.parse_args()
    print(args)
    app = NoteApp(otyp=args.type)
    app.run()


if __name__ == "__main__":
    main()
