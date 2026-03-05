from __future__ import annotations

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.widgets import DataTable, Footer, Header, Input, Label

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
    #project-filter, #note-filter {
        display: none;
        height: 1;
    }
    DataTable {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("n", "new_item", "New"),
        Binding("e", "edit_item", "Edit"),
        Binding("d", "delete_item", "Delete"),
        Binding("s", "search", "Search"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, db_name="project_notes"):
        super().__init__()
        self.db = DB(db_name)
        self._current_project_name: str | None = None
        # Caches for search/filter
        self._project_rows: list[dict] = []
        self._note_rows: list[dict] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="main-panes"):
            with Vertical(id="project-pane"):
                yield Label("Projects", id="project-title")
                yield Input(placeholder="Filter projects...", id="project-filter")
                yield DataTable(id="project-table", cursor_type="row")
            with Vertical(id="note-pane"):
                yield Label("Notes", id="note-title")
                yield Input(placeholder="Filter notes...", id="note-filter")
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
        self._project_rows = []
        for project in self.db.get_projects():
            row = {
                "name": project.name or "",
                "homedir": project.homedir or "",
                "description": project.description or "",
                "key": project.name,
            }
            self._project_rows.append(row)
            table.add_row(row["name"], row["homedir"], key=row["key"])
        # Clear any active filter
        self._hide_filter_widget("project-filter")

    def _refresh_notes(self) -> None:
        table = self.query_one("#note-table", DataTable)
        title = self.query_one("#note-title", Label)
        table.clear()
        self._note_rows = []

        if self._current_project_name is None:
            title.update("Notes")
            return

        title.update(f"Notes for: {self._current_project_name}")
        for note in self.db.get_notes_for_project(self._current_project_name):
            ts = note.timestamp.strftime("%Y-%m-%d %H:%M") if note.timestamp else ""
            comments_full = note.comments or ""
            comments_display = comments_full.replace("\n", " ")
            if len(comments_display) > 60:
                comments_display = comments_display[:57] + "..."
            row = {
                "heading": note.heading or "",
                "ts": ts,
                "comments_display": comments_display,
                "comments_full": comments_full,
                "key": str(note.id),
            }
            self._note_rows.append(row)
            table.add_row(
                row["heading"], row["ts"], row["comments_display"], key=row["key"]
            )
        # Clear any active filter
        self._hide_filter_widget("note-filter")

    # ── Search / filter ────────────────────────────────────

    def action_search(self) -> None:
        """Show the filter bar for the focused pane."""
        table_id = self._focused_table_id()
        if table_id == "project-table":
            filt = self.query_one("#project-filter", Input)
        elif table_id == "note-table":
            filt = self.query_one("#note-filter", Input)
        else:
            return
        filt.display = True
        filt.value = ""
        filt.focus()

    def _hide_filter_widget(self, filter_id: str) -> None:
        """Hide a filter Input and clear its value (no-op if not mounted)."""
        try:
            filt = self.query_one(f"#{filter_id}", Input)
            filt.value = ""
            filt.display = False
        except Exception:
            pass

    @on(Input.Changed, "#project-filter")
    def filter_projects(self, event: Input.Changed) -> None:
        term = event.value.strip().lower()
        self._apply_project_filter(term)

    @on(Input.Changed, "#note-filter")
    def filter_notes(self, event: Input.Changed) -> None:
        term = event.value.strip().lower()
        self._apply_note_filter(term)

    def _apply_project_filter(self, term: str) -> None:
        table = self.query_one("#project-table", DataTable)
        table.clear()
        if not term:
            # Show all rows in original order
            for row in self._project_rows:
                table.add_row(row["name"], row["homedir"], key=row["key"])
            return

        def score(row):
            s = 0
            if term in row["name"].lower():
                s += 2
            if term in row["description"].lower():
                s += 1
            return s

        matches = [
            (row, score(row))
            for row in self._project_rows
            if term in row["name"].lower()
            or term in row["homedir"].lower()
            or term in row["description"].lower()
        ]
        matches.sort(key=lambda x: x[1], reverse=True)
        for row, _ in matches:
            table.add_row(row["name"], row["homedir"], key=row["key"])

    def _apply_note_filter(self, term: str) -> None:
        table = self.query_one("#note-table", DataTable)
        table.clear()
        if not term:
            for row in self._note_rows:
                table.add_row(
                    row["heading"],
                    row["ts"],
                    row["comments_display"],
                    key=row["key"],
                )
            return

        def score(row):
            s = 0
            if term in row["heading"].lower():
                s += 2
            if term in row["comments_full"].lower():
                s += 1
            return s

        matches = [
            (row, score(row))
            for row in self._note_rows
            if term in row["heading"].lower() or term in row["comments_full"].lower()
        ]
        matches.sort(key=lambda x: x[1], reverse=True)
        for row, _ in matches:
            table.add_row(
                row["heading"],
                row["ts"],
                row["comments_display"],
                key=row["key"],
            )

    @on(Input.Submitted, "#project-filter")
    @on(Input.Submitted, "#note-filter")
    def on_filter_submitted(self, event: Input.Submitted) -> None:
        """Enter in the filter bar → dismiss it."""
        self._dismiss_filter(event.input)

    def on_key(self, event: Key) -> None:
        """Escape in the filter bar → dismiss it."""
        if event.key == "escape":
            focused = self.focused
            if isinstance(focused, Input) and focused.id in (
                "project-filter",
                "note-filter",
            ):
                event.prevent_default()
                self._dismiss_filter(focused)

    def _dismiss_filter(self, input_widget: Input) -> None:
        """Hide the filter, show all rows, refocus the table."""
        input_widget.value = ""
        input_widget.display = False
        if input_widget.id == "project-filter":
            self._apply_project_filter("")
            self.query_one("#project-table", DataTable).focus()
        else:
            self._apply_note_filter("")
            self.query_one("#note-table", DataTable).focus()

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
