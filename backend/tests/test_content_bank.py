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
