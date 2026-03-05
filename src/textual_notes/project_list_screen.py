from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.events import Key
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Input, Label

from .db import DB
from .project_detail_screen import ProjectDetailScreen
from .project_screen import build_project_screen


class ProjectListScreen(Screen):
    """Top-level screen listing all projects."""

    CSS = """
    #project-title {
        dock: top;
        height: 1;
        text-style: bold;
        background: $accent;
        color: $text;
        padding: 0 1;
    }
    #project-filter {
        display: none;
        height: 3;
        margin: 0 1;
        border: round $accent;
        background: $surface;
    }
    DataTable {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("plus_sign", "new_project", "New (+)"),
        Binding("e", "edit_project", "Edit"),
        Binding("d", "delete_project", "Delete"),
        Binding("s", "search", "Search"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, db: DB) -> None:
        super().__init__()
        self.db = db
        self._project_rows: list[dict] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical():
            yield Label("Projects", id="project-title")
            yield Input(placeholder="Filter projects...", id="project-filter")
            yield DataTable(id="project-table", cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#project-table", DataTable)
        table.add_columns("Name", "Home Directory")
        self._refresh_projects()
        table.focus()

    # ── Data refresh ──────────────────────────────────────

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
        self._hide_filter_widget()

    # ── Search / filter ───────────────────────────────────

    def action_search(self) -> None:
        filt = self.query_one("#project-filter", Input)
        filt.display = True
        filt.value = ""
        filt.focus()

    def _hide_filter_widget(self) -> None:
        try:
            filt = self.query_one("#project-filter", Input)
            filt.value = ""
            filt.display = False
        except Exception:
            pass

    @on(Input.Changed, "#project-filter")
    def filter_projects(self, event: Input.Changed) -> None:
        term = event.value.strip().lower()
        self._apply_filter(term)

    def _apply_filter(self, term: str) -> None:
        table = self.query_one("#project-table", DataTable)
        table.clear()
        if not term:
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

    @on(Input.Submitted, "#project-filter")
    def on_filter_submitted(self, event: Input.Submitted) -> None:
        self._dismiss_filter()

    def on_key(self, event: Key) -> None:
        if event.key == "escape":
            focused = self.focused
            if isinstance(focused, Input) and focused.id == "project-filter":
                event.prevent_default()
                self._dismiss_filter()

    def _dismiss_filter(self) -> None:
        filt = self.query_one("#project-filter", Input)
        filt.value = ""
        filt.display = False
        self._apply_filter("")
        self.query_one("#project-table", DataTable).focus()

    # ── Row events ────────────────────────────────────────

    @on(DataTable.RowSelected, "#project-table")
    def project_selected(self, event: DataTable.RowSelected) -> None:
        """Enter on a project → drill down to detail screen."""
        if event.row_key is None:
            return
        row_data = event.data_table.get_row(event.row_key)
        project_name = row_data[0]
        self.app.push_screen(
            ProjectDetailScreen(self.db, project_name),
            callback=self._on_detail_dismiss,
        )

    def _on_detail_dismiss(self, result) -> None:
        self._refresh_projects()

    # ── CRUD actions ──────────────────────────────────────

    def action_new_project(self) -> None:
        screen_cls = build_project_screen(self.db)
        self.app.push_screen(screen_cls(), callback=self._on_form_dismiss)

    def action_edit_project(self) -> None:
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
        self.app.push_screen(screen_cls(), callback=self._on_form_dismiss)

    def action_delete_project(self) -> None:
        table = self.query_one("#project-table", DataTable)
        if table.row_count == 0:
            return
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        project = self.db.get_project(row_key.value)
        if project is None:
            return
        project.delete()
        self._refresh_projects()

    def _on_form_dismiss(self, result) -> None:
        if result is not None:
            self._refresh_projects()
