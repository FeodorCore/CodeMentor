-- Таблица пользователей
CREATE TABLE IF NOT EXISTS User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    is_admin BOOLEAN DEFAULT FALSE
);

-- Таблица категорий
CREATE TABLE IF NOT EXISTS Category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

-- Таблица уроков (статей)
CREATE TABLE IF NOT EXISTS Lesson (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES Category(id) ON DELETE CASCADE
);

-- Таблица прогресса пользователя
CREATE TABLE IF NOT EXISTS UserProgress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    lesson_id INTEGER NOT NULL,
    learned BOOLEAN DEFAULT FALSE,
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES Lesson(id) ON DELETE CASCADE,
    UNIQUE(user_id, lesson_id)
);

-- Индексы для скорости
CREATE INDEX IF NOT EXISTS idx_user_telegram_id ON User(telegram_id);
CREATE INDEX IF NOT EXISTS idx_user_username ON User(username);
CREATE INDEX IF NOT EXISTS idx_lesson_category ON Lesson(category_id);
CREATE INDEX IF NOT EXISTS idx_progress_user ON UserProgress(user_id);