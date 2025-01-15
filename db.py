"""
db.py: database interface for the notes project logger
"""

import mongoengine as me

me.connect("project_notes")


class Project(me.Document):
    name = me.StringField(unique=True)


class Note(me.Document):
    project_name = me.StringField()
    timestamp = me.DateTimeField()
    heading = me.StringField()
    comments = me.StringField()


def project_names():
    return [p.name for p in Project.objects.all().order_by("name")]
