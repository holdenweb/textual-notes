# db.py: database interface for the notes project logger
import datetime

import mongoengine as me
import mongomock as mm


class Project(me.Document):
    name = me.StringField(unique=True)
    homedir = me.StringField()
    description = me.StringField()
    timestamp = me.DateTimeField()

    @classmethod
    def names(cls):
        return [p.name for p in cls.objects.all().order_by("name")]


class Note(me.Document):
    project_name = me.StringField()
    timestamp = me.DateTimeField()
    heading = me.StringField()
    comments = me.StringField()


class DB:
    """
    Database access
    """

    def __init__(self, name=None):
        if name is None:
            self.db_name = "** Testing **"
            me.connect(
                "test_connection",
                host="mongodb://localhost",
                mongo_client_class=mm.MongoClient,
            )
        else:
            self.db_name = name
            me.connect(name)

    def project_names(self):
        return [p.name for p in Project.objects.all().order_by("name")]

    # -- Project queries --

    def get_projects(self):
        """Return all projects ordered by name."""
        return Project.objects.all().order_by("name")

    def get_project(self, name):
        """Retrieve a single project by name, or None."""
        try:
            return Project.objects.get(name=name)
        except Project.DoesNotExist:
            return None

    # -- Project mutations --

    def save_project(self, name, homedir, description):
        """Create a new project."""
        new_project = Project(
            name=name,
            timestamp=datetime.datetime.now(),
            homedir=homedir,
            description=description,
        )
        new_project.save()

    def update_project(self, original_name, name, homedir, description):
        """Update an existing project identified by original_name."""
        project = Project.objects.get(name=original_name)
        project.name = name
        project.homedir = homedir
        project.description = description
        project.timestamp = datetime.datetime.now()
        project.save()

    # -- Note queries --

    def get_notes_for_project(self, project_name):
        """Return all notes for a project, most recent first."""
        return Note.objects(project_name=project_name).order_by("-timestamp")

    def get_note(self, note_id):
        """Retrieve a single note by its ObjectId."""
        try:
            return Note.objects.get(id=note_id)
        except Note.DoesNotExist:
            return None

    # -- Note mutations --

    def save_note(self, project_name, heading, comments):
        """Create a new note."""
        new_note = Note(
            project_name=project_name,
            timestamp=datetime.datetime.now(),
            heading=heading,
            comments=comments,
        )
        new_note.save()

    def update_note(self, note_id, project_name, heading, comments):
        """Update an existing note identified by its ObjectId."""
        note = Note.objects.get(id=note_id)
        note.project_name = project_name
        note.heading = heading
        note.comments = comments
        note.timestamp = datetime.datetime.now()
        note.save()
