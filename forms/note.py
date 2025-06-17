# note.py: Note input/edit form for the notes logger project

from textual import on
from db import DB

from textual_forms.form import Form
from textual_forms.field import ChoiceField, StringField, TextField


def build_note_form(db: DB):
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
