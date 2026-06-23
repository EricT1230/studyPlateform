from pathlib import Path
import yaml
from .schema import LoadedQuestion


def load_questions(content_dir: Path) -> list[LoadedQuestion]:
    questions: list[LoadedQuestion] = []
    seen: set[str] = set()
    for yaml_file in sorted(content_dir.glob("*/*.yaml")):
        subject = yaml_file.parent.name
        topic = yaml_file.stem
        raw = yaml.safe_load(yaml_file.read_text(encoding="utf-8")) or []
        for item in raw:
            q = LoadedQuestion(subject=subject, topic=topic, **item)
            if q.id in seen:
                raise ValueError(f"duplicate question id: {q.id}")
            seen.add(q.id)
            questions.append(q)
    return questions
