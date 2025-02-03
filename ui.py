# ui.py: UI components for the notes project logger

from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.widgets import Button, Input, Select, TextArea


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
        self.db.save_note(
            project_name=self.p_select.value,
            heading=self.heading.value,
            comments=self.note_text.text,
        )
        self.app.exit()
