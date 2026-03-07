from __future__ import annotations

from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.screen import ModalScreen

from forms_engine.mongoengine import ModelForm
from textual_wtf import BaseForm, StringField, TextField

from .db import DB, Note
from .styles import FORM_HELP_STYLE, FORM_LABEL_STYLE


def build_note_screen(
    db: DB,
    project_name: str,
    edit_data: dict[str, Any] | None = None,
):
    class NoteForm(ModelForm):
        heading = StringField("Heading")
        comments = TextField("Comments")

        class Meta:
            model = Note
            exclude = ["timestamp", "project_name"]

    class NoteScreen(ModalScreen):
        DEFAULT_CSS = """
NoteScreen {
    align: center middle;
}
#form-container {
    width: 80%;
    height: auto;
    max-height: 80%;
}
FormTextArea {
    min-height: 4;
    height: auto;
}
"""

        def compose(self) -> ComposeResult:
            if edit_data:
                # Strip _id before passing to form — it's only for the update call
                form_data = {k: v for k, v in edit_data.items() if k != "_id"}
                form = NoteForm(
                    data=form_data,
                    title="Edit Note",
                    help_style=FORM_HELP_STYLE,
                    label_style=FORM_LABEL_STYLE,
                )
            else:
                form = NoteForm(
                    title="New Note",
                    help_style=FORM_HELP_STYLE,
                    label_style=FORM_LABEL_STYLE,
                )
            yield form.layout(id="form-container")

        @on(BaseForm.Submitted)
        def submitted(self, event):
            data = event.form.get_data()
            if edit_data and "_id" in edit_data:
                db.update_note(edit_data["_id"], project_name, **data)
            else:
                db.save_note(project_name, **data)
            self.dismiss(data)

        @on(BaseForm.Cancelled)
        def cancelled(self, event):
            self.dismiss(None)

    return NoteScreen
