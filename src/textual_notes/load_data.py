# load_data.py9
import datetime
import json
from importlib.resources import files, as_file
from collections import defaultdict


from textual_notes.db import DB, Note, Project
import textual_notes.fixtures


def load_data():
    def load_docs(df_name, tbl):
        path = files(textual_notes.fixtures).joinpath(df_name)
        with as_file(path) as pth:
            with open(pth) as f:
                data = json.load(f)
            result = []
            for row in data:
                result.append(tbl(**dict(x for x in row.items() if x[0] != "_id")))
        return result

    projects = load_docs("project_notes.project.json", Project)
    project_names = [p["name"] for p in projects]
    notes = load_docs("project_notes.notes.json", Note)
    notes = {note for note in notes if note["project_name"] in project_names}

    for p in Project.objects.all():
        p.delete()
    for p in projects:
        p.save()

    c = defaultdict(int)
    for n in Note.objects.all():
        n.delete()
    for n in notes:
        if n.timestamp is not None:
            n.timestamp = datetime.datetime.strptime(
                n.timestamp["$date"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        c[n.project_name] += 1
        n.save()
    return c


if __name__ == "__main__":
    db = DB()
    c = load_data()
    for project, t in c.items():
        print(f"{project}: {t}")
