import pytest

from app.notes_service import notes_path, read_notes, write_notes


def test_read_missing_returns_empty(tmp_path):
    assert read_notes(tmp_path, "data-structures", "arrays") == ""


def test_write_then_read_roundtrip(tmp_path):
    write_notes(tmp_path, "data-structures", "arrays", "# my note\n")
    assert read_notes(tmp_path, "data-structures", "arrays") == "# my note\n"


def test_write_creates_subject_dir(tmp_path):
    write_notes(tmp_path, "new-subject", "new-topic", "hello")
    assert (tmp_path / "new-subject" / "new-topic.notes.md").exists()


def test_notes_path_location(tmp_path):
    p = notes_path(tmp_path, "english", "vocabulary")
    assert p == tmp_path / "english" / "vocabulary.notes.md"


@pytest.mark.parametrize("bad", ["..", "a/b", "a.b", "x/../y", ".", "", "ok\n"])
def test_bad_segment_rejected(tmp_path, bad):
    with pytest.raises(ValueError):
        notes_path(tmp_path, bad, "ok")
    with pytest.raises(ValueError):
        notes_path(tmp_path, "ok", bad)
