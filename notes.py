import argparse

from textual import on
from textual.app import App
from textual.app import ComposeResult
from textual.containers import Center
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button
from textual.widgets import Input
from textual.widgets import Label
from textual.widgets import Placeholder
from textual.widgets import Select

import db


class UserInterface(Vertical):
    DEFAULT_CSS = """
"""

    def __init__(self, *args, **kwargs):
        """
        Delete if not required
        """
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        self.btn: Button = Button("Submit")
        self.ots = Select([("Note", db.Note)], id="otyp-sel")
        self.ots.border_title = "object type"
        self.ins = Input(id="inst-sel")
        with Vertical():
            yield Placeholder("spacer", id="ph")
            yield Horizontal(self.ots, self.ins, id="selections")
            with Horizontal(id="status"):
                self.splash1 = Splash("Select\nobject\n type", id="splash1")
                yield self.splash1

    @on(Select.Changed)
    def type_selected(self, event: Select.Changed):
        self.type = event.control.value
        status = self.query_one("#status")
        status.remove_children()
        status.mount(Splash("Please select\n an instance"))
        self.ins.focus()


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
        self.ui = UserInterface(id="main-window")
        yield self.ui

    def on_click(self, event):
        self.log(self.tree)
        self.log(self.css_tree)
        self.push_screen(TagSetScreen("overlay", self.ui.splash1))
        self.log("Pause for debugging?")


class TagSetScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def __init__(self, name, loc_widget, *args, **kwargs):
        self.target_region = loc_widget.region
        super().__init__(name, *args, **kwargs)

    def compose(self) -> ComposeResult:
        self.xpos, self.ypos = self.target_region[:2]
        pp = Placeholder(
            "This should appear over the top left of the Splash", id="title"
        )
        pp.styles.offset = self.target_region[:2]
        yield (pp)


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
