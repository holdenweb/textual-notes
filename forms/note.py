# note.py: Note input/edit form for the notes logger project

from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Vertical, Horizontal
from textual.widgets import Button, Input, Select, TextArea

from .project import ProjectScreen


class NoteForm(Vertical):
    DEFAULT_CSS = """\
NoteForm {
    width: 60;
    align: center middle;
    keyline: thin blue;
    & Input, & Select, & TextArea, & Center {
        margin: 1;
    }
    #buttons {
        width: auto;
        height: auto;
    }
    & TextArea {
        min-height: 4;
    }
}
"""

    def __init__(self, db, *args, **kwargs):
        self.db = db
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        projects = self.read_choices()
        self.p_select: Select[str] = Select(projects, prompt="Select Project")
        self.heading: Input = Input(placeholder="Heading")
        self.note_text: TextArea = TextArea()
        self.s_btn: Button = Button("Submit", classes="s-btn")
        self.c_btn: Button = Button("Cancel", classes="c-btn")

        yield self.p_select
        yield self.heading
        yield self.note_text
        with Center():
            with Horizontal(id="buttons"):
                yield self.c_btn
                yield self.s_btn

    def read_choices(self):
        projects = [(n, n) for n in self.db.project_names() if n] + [
            ("<New Project>", "<new>")
        ]
        return projects

    def update_choices(self, result):
        return self.p_select.set_options(self.read_choices())

    @on(Select.Changed)
    async def select_changed(self, m):
        if m.value == "<new>":  # This action only for "New Project"
            proj = await self.app.push_screen(
                ProjectScreen(self.db), self.update_choices
            )
            if proj:
                self.app.notify(f"Project {proj.name!r} added")

    @on(Button.Pressed, ".s-btn")
    def submit_form(self):
        try:
            self.db.save_note(
                project_name=self.p_select.value,
                heading=self.heading.value,
                comments=self.note_text.text,
            )
            self.app.exit()
        except Exception as e:
            self.app.notify(f"I'm so sorry, that failed :-(\n{e}")

    @on(Button.Pressed, ".c-btn")
    def cancel_form(self):
        self.app.exit()
