# app.py: main application logic

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.events import Click
from textual.screen import ModalScreen

from db import DB
from textual_forms import Form, ChoiceField, StringField, TextField


def build_note_screen(db_name, data=None):
    db = DB(db_name)

    def read_choices():
        return [(n, n) for n in db.project_names() if n]

    class NoteForm(Form):
        project_name = ChoiceField(
            read_choices(),
            required=False,
        )
        heading = StringField(placeholder="Heading", required=True)
        comments = TextField()

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def update_choices(self):
            self.fields["project_name"].widget.set_options(read_choices())
            self.fields["project_name"].widget.required = True

    class NoteScreen(ModalScreen):
        DEFAULT_CSS = """
#main-window {
    align: center middle;
}
#form-container {
    width: 80%;
}
"""

        def __init__(self, *args, **kwargs):
            self.data = data
            super().__init__(*args, **kwargs)

        def compose(self) -> ComposeResult:
            with Vertical(id="main-window"):
                yield NoteForm(title="Add Project").render(id="form-container")

        @on(Form.Submitted)
        def submitted(self, event):
            data = event.form.get_data()
            db.save_note(**data)
            self.dismiss(data)

        @on(Form.Cancelled)
        def cancelled(self, event):
            self.screen.dismiss()

        @on(Click)  # For debug only
        def click_response(self, e):
            self.log(self.tree)
            self.log(self.css_tree)

    return NoteScreen
