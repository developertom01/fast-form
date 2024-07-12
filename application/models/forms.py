from pydantic import BaseModel


class FormQuestion(BaseModel):
    id: str
    question: str
    type: str
    is_required: str
    choices: list[str] | None = None


class Form(BaseModel):
    id: str
    title: str
    description: str | None = None
    published_at: str
    create_at: str
    questions: list[FormQuestion]
