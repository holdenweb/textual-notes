"""Note report generation in Markdown, HTML, and PDF formats."""

from __future__ import annotations

import tempfile
import webbrowser
from pathlib import Path

from markdown_it import MarkdownIt
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header, Markdown

from .db import DB

# ── Shared core ────────────────────────────────────────────


def build_report_markdown(db: DB, project_name: str) -> str:
    """Build a Markdown document from all notes in a project."""
    project = db.get_project(project_name)
    lines: list[str] = []

    lines.append(f"# {project_name}")
    if project and project.description:
        lines.append(f"\n*{project.description}*\n")
    lines.append("")

    notes = db.get_notes_for_project(project_name)
    for note in notes:
        ts = note.timestamp.strftime("%d %b %Y %H:%M") if note.timestamp else ""
        lines.append(f"## {note.heading}")
        if ts:
            lines.append(f"*{ts}*\n")
        if note.comments:
            lines.append(note.comments)
        lines.append("")

    return "\n".join(lines)


# ── HTML conversion (shared by browser + PDF) ─────────────

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 48em;
         margin: 2em auto; padding: 0 1em; line-height: 1.6; }}
  h1 {{ border-bottom: 2px solid #333; padding-bottom: 0.3em; }}
  h2 {{ color: #444; margin-top: 1.5em; }}
  h2 + p em {{ color: #888; font-size: 0.9em; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def _markdown_to_html(markdown_text: str, title: str) -> str:
    """Convert a Markdown string to a full HTML document."""
    md = MarkdownIt()
    body_html = md.render(markdown_text)
    return _HTML_TEMPLATE.format(title=title, body=body_html)


# ── Mode A: Textual Markdown screen ───────────────────────


class NoteReportScreen(Screen):
    """Full-screen read-only Markdown report of project notes."""

    CSS = """
    Markdown {
        padding: 1 2;
    }
    """

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
    ]

    def __init__(self, db: DB, project_name: str) -> None:
        super().__init__()
        self.db = db
        self.project_name = project_name

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        md_text = build_report_markdown(self.db, self.project_name)
        yield Markdown(md_text)
        yield Footer()

    def action_go_back(self) -> None:
        self.dismiss(None)


def show_report_screen(app: App, db: DB, project_name: str) -> None:
    """Push the report screen onto the app."""
    app.push_screen(NoteReportScreen(db, project_name))


# ── Mode B: HTML in browser ───────────────────────────────


def open_report_in_browser(db: DB, project_name: str) -> None:
    """Generate HTML from project notes and open in the default browser."""
    md_text = build_report_markdown(db, project_name)
    html = _markdown_to_html(md_text, title=f"Notes: {project_name}")

    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".html",
        prefix=f"notes-{project_name}-",
        delete=False,
    )
    tmp.write(html)
    tmp.close()
    webbrowser.open(f"file://{tmp.name}")


# ── Mode C: PDF ───────────────────────────────────────────


def save_report_as_pdf(db: DB, project_name: str, path: Path | None = None) -> Path:
    """Generate a PDF report. Requires weasyprint."""
    try:
        from weasyprint import HTML  # type: ignore[import-untyped]
    except ImportError:
        raise ImportError(
            "PDF export requires weasyprint. Install with: "
            "uv pip install weasyprint  (also needs: brew install pango)"
        ) from None
    except OSError:
        raise OSError(
            "weasyprint needs system libraries. Install with: brew install pango"
        ) from None

    md_text = build_report_markdown(db, project_name)
    html_str = _markdown_to_html(md_text, title=f"Notes: {project_name}")

    if path is None:
        path = Path(tempfile.mktemp(suffix=".pdf", prefix=f"notes-{project_name}-"))

    HTML(string=html_str).write_pdf(str(path))
    return path
