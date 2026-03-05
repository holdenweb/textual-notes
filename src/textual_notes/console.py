from __future__ import annotations

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Footer, Header, Label

from .db import DB
from .load_data import load_data
from .note_screen import build_note_screen
from .project_screen import build_project_screen


class ConsoleApp(App):
    """Master-detail note-taking application.

    Left pane shows projects, right pane shows notes for the
    selected project. Keys are context-sensitive based on which
    pane has focus.
    """

    TITLE = "Project Notes"

    CSS = """
    #main-panes {
        height: 1fr;
    }
    #project-pane {
        width: 1fr;
        min-width: 25;
        max-width: 50;
        height: 100%;
        border-right: tall $primary;
    }
    #note-pane {
        width: 3fr;
        height: 100%;
    }
    #project-title, #note-title {
        dock: top;
        height: 1;
        text-style: bold;
        background: $accent;
        color: $text;
        padding: 0 1;
    }
    DataTable {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("n", "new_item", "New"),
        Binding("e", "edit_item", "Edit"),
        Binding("d", "delete_item", "Delete"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, db_name="project_notes"):
        super().__init__()
        self.db = DB(db_name)
        self._current_project_name: str | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="main-panes"):
            with Vertical(id="project-pane"):
                yield Label("Projects", id="project-title")
                yield DataTable(id="project-table", cursor_type="row")
            with Vertical(id="note-pane"):
                yield Label("Notes", id="note-title")
                yield DataTable(id="note-table", cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        # Set up project table
        project_table = self.query_one("#project-table", DataTable)
        project_table.add_columns("Name", "Home Directory")
        self._refresh_projects()

        # Set up note table
        note_table = self.query_one("#note-table", DataTable)
        note_table.add_columns("Heading", "Date", "Comments")

        # Focus the project table — this also triggers RowHighlighted
        # for the first row, which loads its notes
        project_table.focus()

    # ── Data refresh ───────────────────────────────────────

    def _refresh_projects(self) -> None:
        table = self.query_one("#project-table", DataTable)
        table.clear()
        for project in self.db.get_projects():
            table.add_row(
                project.name or "",
                project.homedir or "",
                key=project.name,
            )

    def _refresh_notes(self) -> None:
        table = self.query_one("#note-table", DataTable)
        title = self.query_one("#note-title", Label)
        table.clear()

        if self._current_project_name is None:
            title.update("Notes")
            return

        title.update(f"Notes for: {self._current_project_name}")
        for note in self.db.get_notes_for_project(self._current_project_name):
            ts = note.timestamp.strftime("%Y-%m-%d %H:%M") if note.timestamp else ""
            comments = (note.comments or "").replace("\n", " ")
            if len(comments) > 60:
                comments = comments[:57] + "..."
            table.add_row(
                note.heading or "",
                ts,
                comments,
                key=str(note.id),
            )

    # ── Event handlers ─────────────────────────────────────

    @on(DataTable.RowHighlighted, "#project-table")
    def project_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """When cursor moves to a different project, update the notes pane."""
        if event.row_key is None:
            return
        row_data = event.data_table.get_row(event.row_key)
        self._current_project_name = row_data[0]
        self._refresh_notes()

    @on(DataTable.RowSelected, "#project-table")
    def project_selected(self, event: DataTable.RowSelected) -> None:
        """Enter on a project row → edit it."""
        self._edit_project()

    @on(DataTable.RowSelected, "#note-table")
    def note_selected(self, event: DataTable.RowSelected) -> None:
        """Enter on a note row → edit it."""
        self._edit_note()

    # ── Which pane is focused? ─────────────────────────────

    def _focused_table_id(self) -> str | None:
        focused = self.focused
        if isinstance(focused, DataTable):
            return focused.id
        return None

    # ── Context-sensitive actions ──────────────────────────

    def action_new_item(self) -> None:
        table_id = self._focused_table_id()
        if table_id == "project-table":
            self._new_project()
        elif table_id == "note-table":
            self._new_note()

    def action_edit_item(self) -> None:
        table_id = self._focused_table_id()
        if table_id == "project-table":
            self._edit_project()
        elif table_id == "note-table":
            self._edit_note()

    def action_delete_item(self) -> None:
        table_id = self._focused_table_id()
        if table_id == "project-table":
            self._delete_project()
        elif table_id == "note-table":
            self._delete_note()

    # ── Project CRUD ───────────────────────────────────────

    def _new_project(self) -> None:
        screen_cls = build_project_screen(self.db)
        self.push_screen(screen_cls(), callback=self._on_project_dismiss)

    def _edit_project(self) -> None:
        table = self.query_one("#project-table", DataTable)
        if table.row_count == 0:
            return
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        project = self.db.get_project(row_key.value)
        if project is None:
            return
        edit_data = {
            "name": project.name or "",
            "homedir": project.homedir or "",
            "description": project.description or "",
        }
        screen_cls = build_project_screen(self.db, edit_data=edit_data)
        self.push_screen(screen_cls(), callback=self._on_project_dismiss)

    def _on_project_dismiss(self, result) -> None:
        if result is not None:
            self._refresh_projects()
            self._refresh_notes()

    def _delete_project(self) -> None:
        table = self.query_one("#project-table", DataTable)
        if table.row_count == 0:
            return
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        project = self.db.get_project(row_key.value)
        if project is None:
            return
        project.delete()
        self._current_project_name = None
        self._refresh_projects()
        self._refresh_notes()

    # ── Note CRUD ──────────────────────────────────────────

    def _new_note(self) -> None:
        if not self._current_project_name:
            self.notify("Select a project first", severity="warning")
            return
        screen_cls = build_note_screen(self.db, self._current_project_name)
        self.push_screen(screen_cls(), callback=self._on_note_dismiss)

    def _edit_note(self) -> None:
        if not self._current_project_name:
            return
        table = self.query_one("#note-table", DataTable)
        if table.row_count == 0:
            return
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        note = self.db.get_note(row_key.value)
        if note is None:
            return
        edit_data = {
            "_id": str(note.id),
            "heading": note.heading or "",
            "comments": note.comments or "",
        }
        screen_cls = build_note_screen(
            self.db, self._current_project_name, edit_data=edit_data
        )
        self.push_screen(screen_cls(), callback=self._on_note_dismiss)

    def _on_note_dismiss(self, result) -> None:
        if result is not None:
            self._refresh_notes()

    def _delete_note(self) -> None:
        table = self.query_one("#note-table", DataTable)
        if table.row_count == 0:
            return
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        note = self.db.get_note(row_key.value)
        if note is None:
            return
        note.delete()
        self._refresh_notes()


def main():
    DB("project_notes")  # establish connection before loading data
    load_data()
    app = ConsoleApp("project_notes")
    app.run()


if __name__ == "__main__":
    main()
