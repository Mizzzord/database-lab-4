-- Load once after schema.sql into a new database; all people are fictional.
PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;
INSERT INTO Users (user_id, username, email) VALUES
(1, 'alex_ivanov', 'alex@example.com'),
(2, 'maria_petrova', 'maria@example.com'),
(3, 'ivan_sidorov', 'ivan@example.com');
INSERT INTO Projects (project_id, name, description, user_id) VALUES
(1, 'Работа', 'Рабочие задачи Алексея', 1),
(2, 'Личное', 'Личные дела Алексея', 1),
(3, 'Учёба', 'Лабораторные работы Марии', 2);
INSERT INTO Categories (category_id, name, description) VALUES
(1, 'Срочное', 'Требует быстрого выполнения'),
(2, 'Важное', 'Значимо для целей проекта'),
(3, 'Обучение', 'Учебные задания');
INSERT INTO Labels (label_id, name, color) VALUES
(1, 'Bug', '#FF0000'), (2, 'Feature', '#00AA55'), (3, 'Documentation', '#3366FF');
INSERT INTO Tasks (task_id, title, description, due_date, priority, status, user_id, project_id) VALUES
(1, 'Завершить отчёт', 'Подготовить результаты месяца', '2026-11-20', 'high', 'in progress', 1, 1),
(2, 'Купить продукты', NULL, '2026-11-15', 'medium', 'pending', 1, 2),
(3, 'Спроектировать базу данных', 'Нормализовать схему до 3NF', '2026-11-18', 'high', 'completed', 2, 3),
(4, 'Исправить экспорт', 'Проверить кодировку CSV', '2026-11-21', 'high', 'pending', 2, 1),
(5, 'Прочитать документацию SQLite', NULL, NULL, 'low', 'pending', 3, NULL),
(6, 'Описать ER-модель', 'Подготовить диаграмму', '2026-11-18', 'medium', 'completed', 2, 3);
INSERT INTO Task_Categories (task_id, category_id) VALUES
(1, 1), (1, 2), (3, 2), (3, 3), (4, 1), (5, 3), (6, 3);
INSERT INTO Task_Labels (task_id, label_id) VALUES
(1, 3), (3, 2), (3, 3), (4, 1), (5, 3), (6, 3);
COMMIT;
