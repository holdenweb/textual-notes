import json
import sys

import mongoengine as me

from db import Project

if __name__ == "__main__":
    db_name = "project_notes" if len(sys.argv) == 1 else sys.argv[1]

    client = me.connection.MongoClient()
    dbs = {d["name"]: d for d in client.list_databases()}
    if db_name in dbs:
        print(
            f"Database {db_name!r} already exists.\n"
            "Are you happy to destroy all data currently"
            "residing in the database?"
        )
        if input("You must answer YES to continue ... are you SURE? ") != "YES":
            sys.exit("Good decision!")

    me.connect(db_name)

    data = json.load(open("project_notes.project.json"))
    Project.objects.delete()  # Hey, they said YES!
    for d in data:
        del d["_id"]
        Project(**d).save()
