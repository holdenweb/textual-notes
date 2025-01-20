import argparse

from textual.app import App
from textual.app import ComposeResult
from textual.containers import Center
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.widgets import Button
from textual.widgets import Input
from textual.widgets import Label
from textual.widgets import Placeholder
from textual.widgets import Select

import db


class NoteForm(Vertical):
    DEFAULT_CSS = """
"""

    def __init__(self, db, argd=None, *args, **kwargs):
        self.argd = argd
        self.db = db
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        self.btn: Button = Button("Submit")
        ots = Select([], id="otyp-sel")
        ots.border_title = "Select object type"
        ins = Input(id="inst-sel")
        with Vertical():
            yield Horizontal(ots, ins, id="selections")
            with Horizontal(id="status"):
                if not self.argd.type:
                    yield Splash("Please select an object type above")
                else:
                    yield NoteEditor()  # Representing --type=notes --op=edit
                    # but with no instance selected
                    # pretty sure I'm grasping for a generality here ...


class NoteEditor(Horizontal):
    def compose(self) -> ComposeResult:
        yield Vertical(
            Placeholder(id="content"),
            Center(Button("submit"), id="buttonbar"),
            id="info",
        )
        yield Placeholder(id="operations")


class Splash(Center):
    def __init__(self, message, *args, **kwargs):
        self.message = message
        super().__init__(*args, classes="splash-holder", **kwargs)

    def compose(self):
        with Center(classes="splash-holder"):
            yield Label(self.message)


class NoteApp(App):
    CSS_PATH = "x.tcss"

    def __init__(self, argd, *args, **kwargs):
        self.db = db.DB("project_notes")  # This could become a CLI option
        self.argd = argd
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield NoteForm(self.db, argd=self.argd, id="main-window")

    def on_click(self, event):
        self.log(self.tree)
        self.log(self.css_tree)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--type", default=None, help="The object type to be maintained."
    )
    parser.add_argument(
        "--inst", default=None, help="The key of the instance to be maintained."
    )
    args = parser.parse_args()
    print(args)
    app = NoteApp(argd=args)
    app.run()


if __name__ == "__main__":
    main()
