from collections import Counter
from pathlib import Path

from app.content.loader import load_questions


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = REPO_ROOT / "content"


def test_core_graduate_exam_subjects_have_baseline_coverage():
    questions = load_questions(CONTENT_DIR)
    counts = Counter(q.subject for q in questions)

    minimums = {
        "algorithms": 20,
        "computer-organization": 15,
        "data-structures": 20,
        "databases": 20,
        "discrete-math": 15,
        "linear-algebra": 15,
        "machine-learning": 20,
        "networking": 20,
        "operating-systems": 20,
        "probability-statistics": 15,
        "programming": 15,
        "information-security": 15,
    }

    missing = {
        subject: required
        for subject, required in minimums.items()
        if counts[subject] < required
    }

    assert missing == {}


def test_question_bank_has_at_least_one_thousand_questions():
    questions = load_questions(CONTENT_DIR)

    assert len(questions) >= 1000


def test_every_topic_has_tutorial_markdown():
    missing = []
    incomplete = []
    required_sections = ["核心概念", "解題重點", "常見陷阱", "練習前檢查"]

    for yaml_file in sorted(CONTENT_DIR.glob("*/*.yaml")):
        tutorial = yaml_file.with_suffix(".md")
        if not tutorial.exists():
            missing.append(str(tutorial.relative_to(CONTENT_DIR)))
            continue

        markdown = tutorial.read_text(encoding="utf-8")
        missing_sections = [
            section for section in required_sections if section not in markdown
        ]
        if missing_sections:
            incomplete.append(
                {
                    "file": str(tutorial.relative_to(CONTENT_DIR)),
                    "missing_sections": missing_sections,
                }
            )

    assert missing == []
    assert incomplete == []


def test_every_topic_has_english_tutorial_markdown():
    missing = []
    incomplete = []
    required_sections = [
        "Core Concepts",
        "Problem-Solving Focus",
        "Common Pitfalls",
        "Pre-Practice Checklist",
    ]

    for yaml_file in sorted(CONTENT_DIR.glob("*/*.yaml")):
        tutorial = yaml_file.with_name(f"{yaml_file.stem}.en.md")
        if not tutorial.exists():
            missing.append(str(tutorial.relative_to(CONTENT_DIR)))
            continue

        markdown = tutorial.read_text(encoding="utf-8")
        missing_sections = [
            section for section in required_sections if section not in markdown
        ]
        if missing_sections:
            incomplete.append(
                {
                    "file": str(tutorial.relative_to(CONTENT_DIR)),
                    "missing_sections": missing_sections,
                }
            )

    assert missing == []
    assert incomplete == []
