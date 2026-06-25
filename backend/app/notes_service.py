import re
from pathlib import Path

# A path segment must be a single name component with no separators, dots, or
# whitespace. fullmatch (not match) is used so an embedded newline cannot slip
# past a trailing `$` anchor (re's `$` matches just before a final newline).
_SEGMENT = re.compile(r"[A-Za-z0-9_-]+")


def _check(segment: str) -> None:
    if not _SEGMENT.fullmatch(segment):
        raise ValueError(f"invalid path segment: {segment!r}")


def notes_path(content_dir: Path, subject: str, topic: str) -> Path:
    _check(subject)
    _check(topic)
    return content_dir / subject / f"{topic}.notes.md"


def read_notes(content_dir: Path, subject: str, topic: str) -> str:
    p = notes_path(content_dir, subject, topic)
    return p.read_text(encoding="utf-8") if p.exists() else ""


def write_notes(content_dir: Path, subject: str, topic: str, markdown: str) -> None:
    p = notes_path(content_dir, subject, topic)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(markdown, encoding="utf-8")
