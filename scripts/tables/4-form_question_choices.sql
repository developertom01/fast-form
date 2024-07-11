CREATE TABLE IF NOT EXISTS form_question_choices (
    id TEXT NOT NULL PRIMARY KEY,
    choice TEXT NOT NULL,
    question_id TEXT,

    FOREIGN KEY (question_id) REFERENCES form_questions(id)
)