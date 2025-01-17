import db

import rich
from rich.markdown import Markdown


if __name__ == "__main__":
    data = db.DB("project_notes")

    for note in db.Note.objects(project_name="notes"):
        markdown = f"\n\n{note.timestamp:## *%d %b %y* %H:%M}: **{note.heading}**\n"
        rich.print(Markdown(markdown))
        rich.print(Markdown(note.comments))
