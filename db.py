"""
db.py: database interface for the notes project logger
"""

import mongoengine as me


class Project(me.Document):
    name = me.StringField(unique=True)


class Note(me.Document):
    project_name = me.StringField()
    timestamp = me.DateTimeField()
    heading = me.StringField()
    comments = me.StringField()


class DB:
    """
    Database access
    """

    def __init__(self, name):
        self.db_name = name
        me.connect(name)

    def project_names(self):
        return [p.name for p in Project.objects.all().order_by("name")]
