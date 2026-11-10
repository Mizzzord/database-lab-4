-- 1. Tasks with assignee and optional project.
SELECT t.task_id, t.title, u.username, p.name AS project, t.status, t.due_date
FROM Tasks t JOIN Users u ON u.user_id = t.user_id
LEFT JOIN Projects p ON p.project_id = t.project_id ORDER BY t.task_id;
-- 2. Tasks with the category 'Обучение' (M:N).
SELECT t.task_id, t.title FROM Tasks t
JOIN Task_Categories tc ON tc.task_id = t.task_id
JOIN Categories c ON c.category_id = tc.category_id
WHERE c.name = 'Обучение' ORDER BY t.task_id;
-- 3. Open high-priority tasks.
SELECT task_id, title, due_date FROM Tasks
WHERE status <> 'completed' AND priority = 'high' ORDER BY due_date;
-- 4. Include users without tasks in the result.
SELECT u.username, COUNT(t.task_id) AS task_count
FROM Users u LEFT JOIN Tasks t ON t.user_id = u.user_id
GROUP BY u.user_id, u.username ORDER BY u.user_id;
