from typing import Any

from textual import on
from textual.containers import Vertical
from textual.events import Click
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.validation import ValidationResult, Validator

from textual_forms import Form, StringField, TextField

from db import DB


class NonEmpty(Validator):
    def validate(self, value) -> ValidationResult:
        return self.success() if value else self.failure("Cannot be empty")


def build_project_screen(db_name: str, data: dict[str, Any] = None):
    db = DB(db_name)

    class ProjectForm(Form):
        name = StringField(placeholder="Project Name")
        homedir = StringField(placeholder="Home Directory")
        description = TextField()

    class ProjectScreen(ModalScreen):
        DEFAULT_CSS = """
#main-window {
    align: center middle;
}
#form-container {
    width: 80%;
}
"""

        def __init__(self, project=None, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def compose(self) -> ComposeResult:
            with Vertical(id="main-window"):
                yield ProjectForm(title="Add Project").render(id="form-container")

        @on(Form.Submitted)
        def submitted(self, event):
            "Handle submission of a validated form."
            data = event.form.get_data()
            db.save_project(**data)
            self.dismiss(data)

        @on(Form.Cancelled)
        def cancelled(self, event):
            self.dismiss(None)

        @on(Click)  # For debug only
        def click_response(self, e):
            self.log(self.tree)
            self.log(self.css_tree)

    return ProjectScreen
