# note.py: Note input/edit form for the notes logger project

from textual import on
from textual.widgets import Select
from .project import ProjectScreen

from textual_forms.form import Form
from textual_forms.field import ChoiceField, StringField, TextField


def build_note_form(db):
    class NoteForm(Form):
        project_name = ChoiceField(
            choices=[("<New Project>", "<new>")]
            + [(n, n) for n in db.project_names() if n],
            required=True,
        )
        heading = StringField("Heading", required=True)
        comments = TextField()

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.db = db

        def read_choices(self):
            return [("<New Project>", "<new>")] + [
                (n, n) for n in self.db.project_names() if n
            ]

        def update_choices(self):
            return self.fields["project_name"].widget.set_options(
                [("<New Project>", "<new>")]
                + [(n, n) for n in self.db.project_names() if n]
            )

        @on(Select.Changed)
        async def select_changed(self, m):
            if m.value == "<new>":  # This action only for "New Project"
                proj = await self.app.push_screen(
                    ProjectScreen(self.db), self.update_choices
                )  # XXX Should ideally end with new project selected
                if proj:
                    self.app.notify(f"Project {proj.name!r} added")

        @on(Form.Submitted)
        def submit_form(self, event):
            try:
                self.db.save_note(**event.form.get_data())
                self.app.exit()
            except Exception as e:
                self.app.notify(f"I'm so sorry, that failed :-(\n{e}")

        @on(Form.Cancelled)
        def cancel_form(self):
            self.app.exit()

    return NoteForm()
