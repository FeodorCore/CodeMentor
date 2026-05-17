-- Включение поддержки внешних ключей
PRAGMA foreign_keys = ON;

-- Таблица Category (самоссылающаяся)
CREATE TABLE Category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER,
    FOREIGN KEY (parent_id) REFERENCES Category(id) ON DELETE SET NULL
);

-- Таблица Article
CREATE TABLE Article (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    schedule_at DATETIME,
    status TEXT DEFAULT 'draft',
    FOREIGN KEY (category_id) REFERENCES Category(id) ON DELETE CASCADE
);

-- Таблица Question
CREATE TABLE Question (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    FOREIGN KEY (article_id) REFERENCES Article(id) ON DELETE CASCADE
);

-- Таблица Answer
CREATE TABLE Answer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT 0,  -- 0 = false, 1 = true
    FOREIGN KEY (question_id) REFERENCES Question(id) ON DELETE CASCADE
);

-- Таблица Users
CREATE TABLE Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    full_name TEXT,
    is_active BOOLEAN DEFAULT 1
);

-- Таблица UserHistory
CREATE TABLE UserHistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    answer_id INTEGER NOT NULL,
    is_right BOOLEAN NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES Question(id) ON DELETE CASCADE,
    FOREIGN KEY (answer_id) REFERENCES Answer(id) ON DELETE CASCADE
);

-- Таблица MailingLog
CREATE TABLE MailingLog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES Article(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- Индексы для оптимизации запросов по внешним ключам
CREATE INDEX idx_category_parent_id ON Category(parent_id);
CREATE INDEX idx_article_category_id ON Article(category_id);
CREATE INDEX idx_question_article_id ON Question(article_id);
CREATE INDEX idx_answer_question_id ON Answer(question_id);
CREATE INDEX idx_userhistory_user_id ON UserHistory(user_id);
CREATE INDEX idx_userhistory_question_id ON UserHistory(question_id);
CREATE INDEX idx_userhistory_answer_id ON UserHistory(answer_id);
CREATE INDEX idx_mailinglog_article_id ON MailingLog(article_id);
CREATE INDEX idx_mailinglog_user_id ON MailingLog(user_id);