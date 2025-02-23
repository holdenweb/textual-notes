from textual import on
from textual.containers import Horizontal, Center
from textual.widget import Widget
from textual.widgets import Input, Button
from textual.app import ComposeResult
from textual.screen import ModalScreen

from db import Project


class ProjectForm(Widget):
    CSS_PATH = "project.tcss"

    def __init__(self, db, project=None, *args, **kwargs):
        self.project = project if project is not None else Project()
        self.db = db
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        self.xname: Input = Input(
            placeholder="Project Name", value=self.project.name or ""
        )
        self.homedir: Input = Input(
            placeholder="Home Directory", value=self.project.homedir or ""
        )
        self.s_btn: Button = Button("Submit", classes="s-btn")
        self.c_btn: Button = Button("Cancel", classes="c-btn")

        yield self.xname
        yield self.homedir
        with Center():
            with Horizontal(id="buttons"):
                yield self.c_btn
                yield self.s_btn

    @on(Button.Pressed, ".s-btn")
    def submit_form(self):
        try:
            # Assign values to fields
            self.project.name = self.xname.value
            self.project.homedir = self.homedir.value
            # Save the (possibly new) record and return it
            self.project.save()
            self.screen.dismiss(self.project)
        except Exception as e:
            self.app.notify(f"I'm so sorry, that failed :-(\n{e}")

    @on(Button.Pressed, ".c-btn")
    def cancel_form(self):
        self.screen.dismiss()  # No return value => no new record


class ProjectScreen(ModalScreen):
    def __init__(self, db, project=None, *args, **kwargs):
        self.project = project if project is not None else Project()
        self.db = db
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield ProjectForm(self.db, self.project)
