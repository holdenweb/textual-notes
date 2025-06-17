# app.py: main application logic

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.events import Click
from textual.screen import ModalScreen

from db import DB
from textual_forms.form import Form

from forms.note import build_note_form


def build_note_screen(db_name, data=None):
    db = DB(db_name)

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
            self.form = build_note_form(db)

        def compose(self) -> ComposeResult:
            with Vertical(id="main-window"):
                yield self.form.render(id="form-container")

        @on(Form.Submitted)
        def submitted(self, event):
            data = event.form.get_data()
            db.save_note(**data)
            self.app.notify(str(data))
            self.dismiss(data)

        @on(Form.Cancelled)
        def cancelled(self, event):
            self.app.exit()

        @on(Click)  # For debug only
        def click_response(self, e):
            self.log(self.tree)
            self.log(self.css_tree)

    return NoteScreen
