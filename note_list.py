import db


if __name__ == "__main__":
    data = db.DB("project_notes")
    for note in db.Note.objects(project_name="notes"):
        print(f"\n{note.timestamp:%d %b %y %H:%M}: {note.heading}")
        for line in note.comments.splitlines():
            print(line)
