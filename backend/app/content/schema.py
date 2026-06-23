from typing import Literal
from pydantic import BaseModel, model_validator


class Question(BaseModel):
    id: str
    type: Literal["mcq"] = "mcq"
    difficulty: Literal["basic", "intermediate", "advanced", "master"]
    tags: list[str] = []
    question: str
    options: list[str]
    answer: int
    explanation: str = ""

    @model_validator(mode="after")
    def _check(self) -> "Question":
        if len(self.options) < 2:
            raise ValueError("a question needs at least 2 options")
        if not 0 <= self.answer < len(self.options):
            raise ValueError(
                f"answer index {self.answer} out of range for "
                f"{len(self.options)} options"
            )
        return self


class LoadedQuestion(Question):
    subject: str
    topic: str
