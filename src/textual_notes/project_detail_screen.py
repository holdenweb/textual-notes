from __future__ import annotations

from pathlib import Path

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.events import Key
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Input, Label, Static
from textual_fspicker import FileSave, Filters

from .db import DB
from .note_report import open_report_in_browser, save_report_as_pdf, show_report_screen
from .note_screen import build_note_screen


class ProjectDetailScreen(Screen):
    """Detail screen for a single project, showing its notes."""

    CSS = """
    #project-info {
        height: auto;
        padding: 1 2;
        background: $boost;
        border-bottom: tall $primary;
    }
    #project-info Static {
        height: 1;
    }
    #note-title {
        dock: top;
        height: 1;
        text-style: bold;
        background: $accent;
        color: $text;
        padding: 0 1;
    }
    #note-filter {
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
        Binding("plus_sign", "new_note", "New (+)"),
        Binding("e", "edit_note", "Edit"),
        Binding("d", "delete_note", "Delete"),
        Binding("s", "search", "Search"),
        Binding("v", "view_report", "View"),
        Binding("w", "web_report", "Web"),
        Binding("p", "pdf_report", "PDF"),
        Binding("escape", "go_back", "Back"),
    ]

    def __init__(self, db: DB, project_name: str) -> None:
        super().__init__()
        self.db = db
        self.project_name = project_name
        self._note_rows: list[dict] = []

    def compose(self) -> ComposeResult:
        project = self.db.get_project(self.project_name)
        yield Header(show_clock=True)
        with Vertical():
            with Vertical(id="project-info"):
                yield Static(f"Project: {project.name}" if project else "Project: —")
                yield Static(
                    f"Home: {project.homedir}"
                    if project and project.homedir
                    else "Home: —"
                )
                yield Static(
                    f"Description: {project.description}"
                    if project and project.description
                    else "Description: —"
                )
            yield Label("Notes", id="note-title")
            yield Input(placeholder="Filter notes...", id="note-filter")
            yield DataTable(id="note-table", cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        self.app.title = f"Notes — {self.project_name}"
        table = self.query_one("#note-table", DataTable)
        table.add_columns("Heading", "Date", "Comments")
        self._refresh_notes()
        table.focus()

    # ── Data refresh ──────────────────────────────────────

    def _refresh_notes(self) -> None:
        table = self.query_one("#note-table", DataTable)
        table.clear()
        self._note_rows = []
        for note in self.db.get_notes_for_project(self.project_name):
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
        self._hide_filter_widget()

    # ── Search / filter ───────────────────────────────────

    def action_search(self) -> None:
        filt = self.query_one("#note-filter", Input)
        filt.display = True
        filt.value = ""
        filt.focus()

    def _hide_filter_widget(self) -> None:
        try:
            filt = self.query_one("#note-filter", Input)
            filt.value = ""
            filt.display = False
        except Exception:
            pass

    @on(Input.Changed, "#note-filter")
    def filter_notes(self, event: Input.Changed) -> None:
        term = event.value.strip().lower()
        self._apply_filter(term)

    def _apply_filter(self, term: str) -> None:
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

    @on(Input.Submitted, "#note-filter")
    def on_filter_submitted(self, event: Input.Submitted) -> None:
        self._dismiss_filter()

    def on_key(self, event: Key) -> None:
        if event.key == "escape":
            focused = self.focused
            if isinstance(focused, Input) and focused.id == "note-filter":
                event.prevent_default()
                self._dismiss_filter()
                return
            # Not in filter → go back to project list
            event.prevent_default()
            self.dismiss(True)

    def _dismiss_filter(self) -> None:
        filt = self.query_one("#note-filter", Input)
        filt.value = ""
        filt.display = False
        self._apply_filter("")
        self.query_one("#note-table", DataTable).focus()

    # ── Navigation ────────────────────────────────────────

    def action_go_back(self) -> None:
        self.dismiss(True)

    # ── Row events ────────────────────────────────────────

    @on(DataTable.RowSelected, "#note-table")
    def note_selected(self, event: DataTable.RowSelected) -> None:
        """Enter on a note → edit it."""
        self._edit_note()

    # ── CRUD actions ──────────────────────────────────────

    def action_new_note(self) -> None:
        screen_cls = build_note_screen(self.db, self.project_name)
        self.app.push_screen(screen_cls(), callback=self._on_note_dismiss)

    def action_edit_note(self) -> None:
        self._edit_note()

    def _edit_note(self) -> None:
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
        screen_cls = build_note_screen(self.db, self.project_name, edit_data=edit_data)
        self.app.push_screen(screen_cls(), callback=self._on_note_dismiss)

    def action_delete_note(self) -> None:
        table = self.query_one("#note-table", DataTable)
        if table.row_count == 0:
            return
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        note = self.db.get_note(row_key.value)
        if note is None:
            return
        note.delete()
        self._refresh_notes()

    def _on_note_dismiss(self, result) -> None:
        if result is not None:
            self._refresh_notes()

    # ── Report actions ────────────────────────────────────

    def action_view_report(self) -> None:
        show_report_screen(self.app, self.db, self.project_name)

    def action_web_report(self) -> None:
        open_report_in_browser(self.db, self.project_name)

    @work
    async def action_pdf_report(self) -> None:
        save_path: Path | None = await self.app.push_screen_wait(
            FileSave(
                location=Path.cwd(),
                default_file=f"notes-{self.project_name}.pdf",
                filters=Filters(
                    ("PDF files", lambda p: p.suffix.lower() == ".pdf"),
                ),
            )
        )
        if save_path is None:
            return
        # Ensure a .pdf extension
        if not save_path.suffix:
            save_path = save_path.with_suffix(".pdf")
        elif save_path.suffix.lower() != ".pdf":
            confirmed = await self._confirm_suffix(save_path)
            if not confirmed:
                return
        self.run_worker(lambda: self._generate_pdf(save_path), thread=True)

    async def _confirm_suffix(self, path: Path) -> bool:
        """Ask the user to confirm a non-.pdf file extension."""
        from textual.screen import ModalScreen
        from textual.widgets import Button

        class ConfirmSuffix(ModalScreen[bool]):
            CSS = """
            ConfirmSuffix {
                align: center middle;
            }
            #confirm-box {
                width: 60;
                height: auto;
                padding: 1 2;
                background: $surface;
                border: round $accent;
            }
            #confirm-box Button {
                margin: 1 1 0 0;
            }
            """

            def compose(self):
                from textual.containers import Horizontal

                with Vertical(id="confirm-box"):
                    yield Static(
                        f'File will be saved as "{path.name}" '
                        f"(extension: {path.suffix}).\n\n"
                        "PDF reports normally use a .pdf extension.\n"
                        "Save with this extension anyway?"
                    )
                    with Horizontal():
                        yield Button("Save anyway", id="yes", variant="primary")
                        yield Button("Cancel", id="no")

            @on(Button.Pressed, "#yes")
            def confirm(self, event: Button.Pressed) -> None:
                self.dismiss(True)

            @on(Button.Pressed, "#no")
            def cancel(self, event: Button.Pressed) -> None:
                self.dismiss(False)

        return await self.app.push_screen_wait(ConfirmSuffix())

    def _generate_pdf(self, path: Path) -> None:
        try:
            result = save_report_as_pdf(self.db, self.project_name, path=path)
            self.notify(f"PDF saved to {result}")
        except (ImportError, OSError) as exc:
            self.notify(str(exc), severity="error")
