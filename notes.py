import datetime
import sys

from textual.app import App
from textual.app import ComposeResult
from textual.app import on
from textual.containers import Center
from textual.containers import Vertical
from textual.widgets import Button
from textual.widgets import Input
from textual.widgets import Select
from textual.widgets import TextArea

import db


class NoteForm(Vertical):
    DEFAULT_CSS = """\
NoteForm {
    width: 60;
    height: 20;
    align: center middle;
    keyline: thin blue;
    & Input, & Select, & TextArea, & Center {
        margin: 1;
    }
}
"""

    def __init__(self, db, *args, **kwargs):
        self.db = db
        super().__init__()

    def compose(self) -> ComposeResult:
        projects = [(n, n) for n in self.db.project_names()]
        self.p_select: Select[str] = Select(projects, prompt="Select Project")
        self.heading: Input = Input(placeholder="Heading")
        self.note_text: TextArea = TextArea()
        self.btn: Button = Button("Submit")
        yield self.p_select
        yield self.heading
        yield self.note_text
        yield Center(self.btn)

    @on(Button.Pressed)
    def submit_form(self):
        new_note = db.Note(
            project_name=self.p_select.value,
            timestamp=datetime.datetime.now(),
            heading=self.heading.value,
            comments=self.note_text.text,
        )
        new_note.save()
        self.app.exit()


class NoteApp(App):
    DEFAULT_CSS = """
#main-window {
    align: center middle;
}
"""

    def compose(self) -> ComposeResult:
        self.db = db.DB("project_notes")
        with Vertical(id="main-window"):
            yield NoteForm(self.db)

    def on_click(self, event):
        self.log(self.tree)
        self.log(self.css_tree)


def main(args):
    app = NoteApp()
    app.run()


if __name__ == "__main__":
    main(sys.argv)
