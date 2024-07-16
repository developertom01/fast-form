CREATE TABLE IF NOT EXISTS form_questions (
    id TEXT NOT NULL PRIMARY KEY,
    question TEXT NOT NULL,
    type VARCHAR(10) NOT NULL,
    is_required BOOLEAN NOT NULL,
    form_id TEXT,
    
    FOREIGN KEY (form_id) REFERENCES forms(id) ON DELETE CASCADE
)