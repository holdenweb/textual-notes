import sys

import mongoengine as me

from db import Project

PROJECTS = """\
local software
dotfiles
notes""".splitlines()

if __name__ == "__main__":

    db_name = "project_notes" if len(sys.argv) == 1 else sys.argv[1]

    client = me.connection.MongoClient()
    dbs = {d["name"]: d for d in client.list_databases()}
    if db_name in dbs:
        sys.exit(
            f"Database {db_name!r} already exists.\n"
            "Manual deletion is currently the only solution, sorry."
        )

    me.connect(db_name)
    for name in PROJECTS:
        Project(name=name).save()
