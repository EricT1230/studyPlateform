from datetime import date, timedelta


INTERVALS = {1: 1, 2: 3, 3: 7, 4: 16, 5: 35}
MAX_BOX = 5


def next_schedule(current_box: int, is_correct: bool, today: date) -> tuple[int, date]:
    """Compute the next Leitner box and due date.

    current_box is the box before this answer. Callers should pass box 1 for
    a question that has never been scheduled.
    """
    if is_correct:
        new_box = min(current_box + 1, MAX_BOX)
    else:
        new_box = 1

    new_due = today + timedelta(days=INTERVALS[new_box])
    return new_box, new_due
