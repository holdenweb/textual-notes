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


def build_project_form(db: DB):
    class ProjectForm(Form):
        DEFAULT_CSS = """
    ProjectForm {
        width: 50;
        align: center middle;
        keyline: thin blue;
        & Input, & Select, & TextArea, & Center {
            margin: 1;
        }
        #buttons {
            width: 75%;
            height: auto;
        }
    }
    """
        name = StringField()
        homedir = StringField()
        description = TextField()

        def __init__(self, *args, **kwargs):
            self.db = db
            super().__init__(*args, **kwargs)

        @on(Form.Submitted)
        def submit_form(self, event):
            try:
                self.db.save_project(**event.form.get_data())
                self.app.exit()
            except Exception as e:
                self.app.notify(f"I'm so sorry, that failed :-(\n{e}")

        @on(Form.Cancelled)
        def cancel_form(self):
            self.screen.dismiss()  # No return value => no new record

    return ProjectForm()


def build_project_screen(db_name, data=None):
    db = DB(db_name)

    class ProjectScreen(ModalScreen):
        DEFAULT_CSS = """
    ProjectScreen {
        align: center middle;
        width: 35;
    }
    """

        def __init__(self, project=None, *args, **kwargs):
            self.db = db
            super().__init__(*args, **kwargs)

        def compose(self) -> ComposeResult:
            with Vertical(id="main-window"):
                yield build_project_form(self.db).render(id="form-container")

        @on(Form.Submitted)
        def submitted(self, event):
            data = event.form.get_data()
            db.save_project(**data)
            self.app.notify(str(data))
            self.dismiss(data)

        @on(Form.Cancelled)
        def cancelled(self, event):
            self.app.exit()

        @on(Click)  # For debug only
        def click_response(self, e):
            self.log(self.tree)
            self.log(self.css_tree)

    return ProjectScreen
