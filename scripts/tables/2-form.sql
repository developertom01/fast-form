CREATE TABLE IF NOT EXISTS forms (
    id TEXT NOT NULL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    user_id TEXT,
    published_at DATETIME,
    created_at DATETIME,
    published_key TEXT,

    FOREIGN KEY (user_id) REFERENCES users(id)
)