-- SQLite: run against a new database. Enable foreign keys on EVERY connection.
PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE CHECK (length(trim(username)) > 0),
    email TEXT NOT NULL UNIQUE CHECK (length(trim(email)) > 0),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE Projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    description TEXT,
    user_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);
CREATE TABLE Categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) > 0),
    description TEXT
);
CREATE TABLE Labels (
    label_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) > 0),
    color TEXT NOT NULL DEFAULT '#808080'
        CHECK (length(color) = 7 AND substr(color, 1, 1) = '#'
               AND substr(color, 2) NOT GLOB '*[^0-9A-Fa-f]*')
);
CREATE TABLE Tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    description TEXT,
    due_date TEXT,
    priority TEXT NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in progress', 'completed')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    user_id INTEGER NOT NULL,
    project_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES Projects(project_id) ON DELETE SET NULL
);
CREATE TABLE Task_Categories (
    task_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    PRIMARY KEY (task_id, category_id),
    FOREIGN KEY (task_id) REFERENCES Tasks(task_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id) ON DELETE CASCADE
);
CREATE TABLE Task_Labels (
    task_id INTEGER NOT NULL,
    label_id INTEGER NOT NULL,
    PRIMARY KEY (task_id, label_id),
    FOREIGN KEY (task_id) REFERENCES Tasks(task_id) ON DELETE CASCADE,
    FOREIGN KEY (label_id) REFERENCES Labels(label_id) ON DELETE CASCADE
);

CREATE INDEX idx_tasks_user_id ON Tasks(user_id);
CREATE INDEX idx_tasks_project_id ON Tasks(project_id);
CREATE INDEX idx_tasks_due_date ON Tasks(due_date);
CREATE INDEX idx_tasks_status ON Tasks(status);
CREATE INDEX idx_projects_user_id ON Projects(user_id);
-- Composite primary keys cover searches by task_id; these cover reverse traversal.
CREATE INDEX idx_task_categories_category_id ON Task_Categories(category_id);
CREATE INDEX idx_task_labels_label_id ON Task_Labels(label_id);
COMMIT;
