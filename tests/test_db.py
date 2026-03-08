"""TDD tests for DB timestamp and modified-date behaviour.

Written RED-first: these tests describe the *desired* behaviour.
Run them, watch them fail, then fix the code until they pass.
"""

import datetime
import time

from textual_notes.db import Project


# ── Helper ────────────────────────────────────────────────


def _small_delay():
    """Sleep just long enough for datetime.now() to advance."""
    time.sleep(0.05)


# ══════════════════════════════════════════════════════════
# PROJECT — creation
# ══════════════════════════════════════════════════════════


class TestProjectCreation:
    def test_new_project_has_timestamp(self, db):
        db.save_project("P1", "/tmp", "desc")
        p = db.get_project("P1")
        assert p.timestamp is not None

    def test_new_project_has_modified(self, db):
        db.save_project("P1", "/tmp", "desc")
        p = db.get_project("P1")
        assert p.modified is not None

    def test_new_project_timestamp_equals_modified(self, db):
        db.save_project("P1", "/tmp", "desc")
        p = db.get_project("P1")
        assert p.timestamp == p.modified


# ══════════════════════════════════════════════════════════
# PROJECT — update with real changes
# ══════════════════════════════════════════════════════════


class TestProjectUpdateWithChanges:
    def test_modified_advances_on_change(self, db):
        db.save_project("P1", "/tmp", "old desc")
        p = db.get_project("P1")
        original_modified = p.modified
        _small_delay()

        db.update_project("P1", "P1", "/tmp", "new desc")

        p = db.get_project("P1")
        assert p.modified is not None
        assert p.modified > original_modified

    def test_timestamp_unchanged_on_update(self, db):
        db.save_project("P1", "/tmp", "old desc")
        p = db.get_project("P1")
        original_ts = p.timestamp
        _small_delay()

        db.update_project("P1", "P1", "/tmp", "new desc")

        p = db.get_project("P1")
        assert p.timestamp == original_ts

    def test_rename_updates_modified(self, db):
        db.save_project("P1", "/tmp", "desc")
        p = db.get_project("P1")
        original_modified = p.modified
        _small_delay()

        db.update_project("P1", "P1-renamed", "/tmp", "desc")

        p = db.get_project("P1-renamed")
        assert p.modified > original_modified

    def test_field_values_persisted(self, db):
        db.save_project("P1", "/tmp", "old")
        db.update_project("P1", "P1", "/new", "new")

        p = db.get_project("P1")
        assert p.homedir == "/new"
        assert p.description == "new"


# ══════════════════════════════════════════════════════════
# PROJECT — update with NO changes (should be a no-op)
# ══════════════════════════════════════════════════════════


class TestProjectUpdateNoChanges:
    def test_modified_unchanged_when_nothing_changed(self, db):
        db.save_project("P1", "/tmp", "desc")
        p = db.get_project("P1")
        original_modified = p.modified
        _small_delay()

        db.update_project("P1", "P1", "/tmp", "desc")

        p = db.get_project("P1")
        assert p.modified == original_modified


# ══════════════════════════════════════════════════════════
# PROJECT — legacy records (no modified field in DB)
# ══════════════════════════════════════════════════════════


class TestProjectLegacy:
    def test_update_legacy_project_sets_modified(self, db):
        """A project created before the modified field existed."""
        # Insert directly via MongoEngine, without setting modified
        old_ts = datetime.datetime(2024, 1, 1, 12, 0, 0)
        p = Project(name="Legacy", homedir="/old", description="old", timestamp=old_ts)
        p.save()

        # Verify it has no modified
        p = db.get_project("Legacy")
        assert p.modified is None

        # Now update it
        db.update_project("Legacy", "Legacy", "/old", "updated desc")

        p = db.get_project("Legacy")
        assert p.modified is not None
        assert p.timestamp == old_ts  # created date untouched


# ══════════════════════════════════════════════════════════
# PROJECT — None vs "" edge case
# ══════════════════════════════════════════════════════════


class TestProjectNoneVsEmpty:
    def test_none_homedir_vs_empty_string_is_no_change(self, db):
        """A project with homedir=None updated with homedir='' is NOT
        a real change — both mean 'no home directory'."""
        old_ts = datetime.datetime(2024, 1, 1, 12, 0, 0)
        p = Project(
            name="NoneDir",
            homedir=None,
            description="desc",
            timestamp=old_ts,
            modified=old_ts,
        )
        p.save()
        _small_delay()

        # Form will send "" for an empty field, not None
        db.update_project("NoneDir", "NoneDir", "", "desc")

        p = db.get_project("NoneDir")
        assert p.modified == old_ts  # should NOT have changed

    def test_none_description_vs_empty_string_is_no_change(self, db):
        old_ts = datetime.datetime(2024, 1, 1, 12, 0, 0)
        p = Project(
            name="NoneDesc",
            homedir="/tmp",
            description=None,
            timestamp=old_ts,
            modified=old_ts,
        )
        p.save()
        _small_delay()

        db.update_project("NoneDesc", "NoneDesc", "/tmp", "")

        p = db.get_project("NoneDesc")
        assert p.modified == old_ts  # should NOT have changed


# ══════════════════════════════════════════════════════════
# NOTE — creation
# ══════════════════════════════════════════════════════════


class TestNoteCreation:
    def test_new_note_has_timestamp_and_modified(self, db):
        db.save_note("P1", "heading", "body")
        notes = list(db.get_notes_for_project("P1"))
        assert len(notes) == 1
        n = notes[0]
        assert n.timestamp is not None
        assert n.modified is not None
        assert n.timestamp == n.modified


# ══════════════════════════════════════════════════════════
# NOTE — update with real changes
# ══════════════════════════════════════════════════════════


class TestNoteUpdateWithChanges:
    def test_modified_advances_on_change(self, db):
        db.save_note("P1", "old heading", "body")
        n = list(db.get_notes_for_project("P1"))[0]
        original_modified = n.modified
        _small_delay()

        db.update_note(str(n.id), "P1", "new heading", "body")

        n = db.get_note(str(n.id))
        assert n.modified > original_modified

    def test_timestamp_unchanged_on_note_update(self, db):
        db.save_note("P1", "heading", "old body")
        n = list(db.get_notes_for_project("P1"))[0]
        original_ts = n.timestamp
        _small_delay()

        db.update_note(str(n.id), "P1", "heading", "new body")

        n = db.get_note(str(n.id))
        assert n.timestamp == original_ts


# ══════════════════════════════════════════════════════════
# NOTE — update with NO changes
# ══════════════════════════════════════════════════════════


class TestNoteUpdateNoChanges:
    def test_modified_unchanged_when_nothing_changed(self, db):
        db.save_note("P1", "heading", "body")
        n = list(db.get_notes_for_project("P1"))[0]
        original_modified = n.modified
        _small_delay()

        db.update_note(str(n.id), "P1", "heading", "body")

        n = db.get_note(str(n.id))
        assert n.modified == original_modified
