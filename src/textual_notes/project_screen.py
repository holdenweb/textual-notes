from __future__ import annotations

from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.screen import ModalScreen

from forms_engine.mongoengine import ModelForm
from textual_wtf import BaseForm, StringField, TextField

from .db import DB, Project
from .styles import FORM_HELP_STYLE, FORM_LABEL_STYLE


class ProjectForm(ModelForm):
    name = StringField("Project Name")
    homedir = StringField("Home Directory")
    description = TextField("Description")

    class Meta:
        model = Project
        exclude = ["timestamp"]


def build_project_screen(db: DB, edit_data: dict[str, Any] | None = None):
    class ProjectScreen(ModalScreen):
        DEFAULT_CSS = """
ProjectScreen {
    align: center middle;
}
#form-container {
    width: 80%;
    height: auto;
    max-height: 80%;
}
"""

        def compose(self) -> ComposeResult:
            if edit_data:
                form = ProjectForm(
                    data=edit_data,
                    title="Edit Project",
                    help_style=FORM_HELP_STYLE,
                    label_style=FORM_LABEL_STYLE,
                )
            else:
                form = ProjectForm(
                    title="New Project",
                    help_style=FORM_HELP_STYLE,
                    label_style=FORM_LABEL_STYLE,
                )
            yield form.layout(id="form-container")

        @on(BaseForm.Submitted)
        def submitted(self, event):
            data = event.form.get_data()
            if edit_data:
                db.update_project(edit_data["name"], **data)
            else:
                db.save_project(**data)
            self.dismiss(data)

        @on(BaseForm.Cancelled)
        def cancelled(self, event):
            self.dismiss(None)

    return ProjectScreen
