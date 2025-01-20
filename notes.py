import argparse

from textual.app import App
from textual.app import ComposeResult
from textual.containers import Center
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.widgets import Button
from textual.widgets import Input
from textual.widgets import Label
from textual.widgets import Select

import db


class Skeleton(Vertical):
    DEFAULT_CSS = """
"""

    def __init__(self, *args, **kwargs):
        """
        Delete if not required
        """
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        self.btn: Button = Button("Submit")
        ots = Select([("Note", db.Note)], id="otyp-sel")
        ots.border_title = "object type"
        ins = Input(id="inst-sel")
        with Vertical():
            yield Horizontal(ots, ins, id="selections")
            with Horizontal(id="status"):
                yield Splash("Select\nobject\n type")


class Splash(Center):
    def __init__(self, message, *args, **kwargs):
        self.message = message
        super().__init__(*args, classes="splash-holder", **kwargs)

    def compose(self):
        yield Label(self.message)


class NoteApp(App):
    CSS_PATH = "x.tcss"

    def __init__(self, argd, *args, **kwargs):
        self.db = db.DB("project_notes")  # This could become a CLI option
        self.argd = argd
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Skeleton(id="main-window")

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
