import sys


import db


if __name__ == "__main__":
    data = db.DB("project_notes")

    if len(sys.argv) == 2:
        pname = sys.argv[1]
    elif len(sys.argv) == 1:
        pname = "notes"
    else:
        sys.exit("Can't handle  multiple arguments")
    for note in db.Note.objects(project_name=pname):
        markdown = f"\n\n{note.timestamp:## *%d %b %y* %H:%M}: **{note.heading}**\n"
        print(markdown)
        print(note.comments)
        # rich.print(Markdown(markdown))
        # rich.print(Markdown(note.comments))
