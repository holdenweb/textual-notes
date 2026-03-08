import pytest

from textual_notes.db import DB, Note, Project


@pytest.fixture()
def db():
    """Provide a clean mongomock-backed DB for each test."""
    database = DB()  # name=None → uses mongomock
    # Drop all documents between tests so each test starts clean
    Project.drop_collection()
    Note.drop_collection()
    return database
