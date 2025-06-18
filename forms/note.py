# note.py: Note input/edit form for the notes logger project

from textual import on
from db import DB

from textual_forms.form import Form
from textual_forms.field import ChoiceField, StringField, TextField


def build_note_form(db: DB):
    class NoteForm(Form):
        project_name = ChoiceField(
            [(n, n) for n in db.project_names() if n],
            required=False,
        )
        heading = StringField(placeholder="Heading", required=True)
        comments = TextField()

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @classmethod
        def read_choices(cls):
            return [(n, n) for n in db.project_names() if n]

        def update_choices(self):
            self.fields["project_name"].widget.set_options(self.read_choices())
            self.fields["project_name"].widget.required = True

        def on_mount(self):
            self.update_choices()

        @on(Form.Submitted)
        def submit_form(self, event):
            try:
                self.db.save_note(**event.form.get_data())
                self.app.exit()
            except Exception as e:
                self.app.notify(f"I'm so sorry, that failed :-(\n{e}")

        @on(Form.Cancelled)
        def cancel_form(self):
            self.screen.dismiss()

    return NoteForm(title="Add Note")
