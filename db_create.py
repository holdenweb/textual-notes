import mongoengine as me

from db import Project

me.connect("project_notes")

PROJECTS = """\
local software
dotfiles
notes""".splitlines()

for name in PROJECTS:
    Project(name=name).save()
