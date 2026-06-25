from datetime import date, timedelta

from app.scheduler_service import INTERVALS, MAX_BOX, next_schedule


TODAY = date(2026, 6, 24)


def test_correct_promotes_one_box():
    box, due = next_schedule(2, True, TODAY)
    assert box == 3
    assert due == TODAY + timedelta(days=INTERVALS[3])


def test_wrong_resets_to_box_one():
    box, due = next_schedule(4, False, TODAY)
    assert box == 1
    assert due == TODAY + timedelta(days=1)


def test_correct_caps_at_max_box():
    box, due = next_schedule(MAX_BOX, True, TODAY)
    assert box == MAX_BOX
    assert due == TODAY + timedelta(days=INTERVALS[MAX_BOX])


def test_first_correct_vs_first_wrong_differ():
    # A never-scheduled question is passed current_box=1 by the caller.
    correct_box, correct_due = next_schedule(1, True, TODAY)
    wrong_box, wrong_due = next_schedule(1, False, TODAY)
    assert correct_box == 2 and correct_due == TODAY + timedelta(days=3)
    assert wrong_box == 1 and wrong_due == TODAY + timedelta(days=1)


def test_intervals_match_spec():
    # Lock the Leitner intervals to literal values so a typo in INTERVALS
    # cannot pass unnoticed (the due-date assertions above reference INTERVALS
    # itself, so they would not catch a wrong value for box 3/4/5).
    assert INTERVALS == {1: 1, 2: 3, 3: 7, 4: 16, 5: 35}
    assert MAX_BOX == 5
