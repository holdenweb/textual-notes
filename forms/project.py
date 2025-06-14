from textual import on
from textual.containers import Horizontal, Center, Vertical
from textual.widgets import Input, Button
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.validation import ValidationResult, Validator

from db import Project


class NonEmpty(Validator):
    def validate(self, value) -> ValidationResult:
        return self.success() if value else self.failure("Cannot be empty")


class ProjectForm(Vertical):
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

    def __init__(self, db, project=None, *args, **kwargs):
        self.project = project if project is not None else Project()
        self.db = db
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        self.pr_name: Input = Input(
            placeholder="Project Name",
            value=self.project.name or "",
            validators=[NonEmpty()],
            validate_on=["changed"],
        )
        self.pr_homedir: Input = Input(
            placeholder="Home Directory", value=self.project.homedir or ""
        )
        self.s_btn: Button = Button("Submit", classes="s-btn")
        self.c_btn: Button = Button("Cancel", classes="c-btn")

        yield self.pr_name
        yield self.pr_homedir
        with Center():
            with Horizontal(id="buttons"):
                yield self.c_btn
                yield self.s_btn

    @on(Button.Pressed, ".s-btn")
    def submit_form(self):
        try:
            # Assign values to fields
            self.project.name = self.validate_field(self.pr_name)
            self.project.homedir = self.pr_homedir.value
            if self.project.name.is_valid() and self.project.homedir.is_valid():
                # Save the (possibly new) record and return it
                self.project.save()
                self.screen.dismiss(self.project)
        except Exception as e:
            self.app.notify(f"I'm so sorry, that failed :-(\n{e}")

    def validate_field(self, field):
        if not field.validate(field.value):
            raise ValueError("Field does not validate")
        return field.value

    @on(Button.Pressed, ".c-btn")
    def cancel_form(self):
        self.screen.dismiss()  # No return value => no new record


class ProjectScreen(ModalScreen):
    DEFAULT_CSS = """
ProjectScreen {
    align: center middle;
    width: 35;
}
"""

    def __init__(self, db, project=None, *args, **kwargs):
        self.project = project if project is not None else Project()
        self.db = db
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        with Vertical(id="main-window"):
            yield ProjectForm(self.db, self.project)
