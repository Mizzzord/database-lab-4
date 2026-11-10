from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        for name in ('schema.sql', 'seed_data.sql'):
            self.db.executescript((ROOT / 'database' / name).read_text(encoding='utf-8'))
        self.addCleanup(self.db.close)

    def scalar(self, sql, params=()):
        return self.db.execute(sql, params).fetchone()[0]

    def rejects(self, sql, params=()):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(sql, params)

    def test_schema_and_seed(self):
        expected = {'Users': 3, 'Projects': 3, 'Categories': 3, 'Labels': 3,
                    'Tasks': 6, 'Task_Categories': 7, 'Task_Labels': 6}
        for table, count in expected.items():
            self.assertEqual(self.scalar(f'SELECT COUNT(*) FROM {table}'), count)
        self.assertEqual(self.scalar('PRAGMA foreign_keys'), 1)
        self.assertEqual(self.scalar('PRAGMA integrity_check'), 'ok')
        self.assertEqual(self.db.execute('PRAGMA foreign_key_check').fetchall(), [])

    def test_many_to_many_and_duplicate_pairs(self):
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM Task_Categories WHERE task_id=3'), 2)
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM Task_Labels WHERE task_id=3'), 2)
        self.rejects('INSERT INTO Task_Categories VALUES (3, 2)')
        self.rejects('INSERT INTO Task_Labels VALUES (3, 2)')

    def test_foreign_keys_on_every_relation(self):
        for sql in ["INSERT INTO Projects(name,user_id) VALUES ('X',999)",
                    "INSERT INTO Tasks(title,user_id) VALUES ('X',999)",
                    "INSERT INTO Tasks(title,user_id,project_id) VALUES ('X',1,999)",
                    'INSERT INTO Task_Categories VALUES (999,1)',
                    'INSERT INTO Task_Categories VALUES (1,999)',
                    'INSERT INTO Task_Labels VALUES (999,1)',
                    'INSERT INTO Task_Labels VALUES (1,999)']:
            with self.subTest(sql=sql):
                self.rejects(sql)

    def test_required_fields_and_enumerations(self):
        for sql in ["UPDATE Tasks SET title='  ' WHERE task_id=1",
                    "UPDATE Tasks SET priority='urgent' WHERE task_id=1",
                    "UPDATE Tasks SET status='unknown' WHERE task_id=1",
                    'UPDATE Tasks SET priority=NULL WHERE task_id=1',
                    'UPDATE Tasks SET status=NULL WHERE task_id=1',
                    'UPDATE Tasks SET user_id=NULL WHERE task_id=1',
                    'INSERT INTO Task_Categories VALUES (NULL,1)',
                    'INSERT INTO Task_Labels VALUES (1,NULL)',
                    "UPDATE Labels SET color='#GG0000' WHERE label_id=1",
                    "UPDATE Labels SET color='#123' WHERE label_id=1"]:
            with self.subTest(sql=sql):
                self.rejects(sql)

    def test_unique_identifiers(self):
        self.rejects("INSERT INTO Users(username,email) VALUES ('alex_ivanov','other@example.com')")
        self.rejects("INSERT INTO Users(username,email) VALUES ('other','alex@example.com')")
        self.rejects("INSERT INTO Categories(name) VALUES ('Срочное')")
        self.rejects("INSERT INTO Labels(name) VALUES ('Bug')")

    def test_defaults_and_optional_project(self):
        self.db.execute("INSERT INTO Tasks(title,user_id) VALUES ('Новая',1)")
        row = self.db.execute('SELECT priority,status,project_id,created_at,updated_at FROM Tasks WHERE task_id=7').fetchone()
        self.assertEqual(row[:3], ('medium', 'pending', None))
        self.assertTrue(row[3] and row[4])

    def test_project_delete_keeps_tasks(self):
        self.db.execute('DELETE FROM Projects WHERE project_id=1')
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM Tasks'), 6)
        self.assertIsNone(self.scalar('SELECT project_id FROM Tasks WHERE task_id=4'))

    def test_task_delete_cascades_links(self):
        self.db.execute('DELETE FROM Tasks WHERE task_id=3')
        for table in ('Task_Categories', 'Task_Labels'):
            self.assertEqual(self.scalar(f'SELECT COUNT(*) FROM {table} WHERE task_id=3'), 0)
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM Categories'), 3)

    def test_dictionary_delete_keeps_tasks(self):
        self.db.execute('DELETE FROM Categories WHERE category_id=3')
        self.db.execute('DELETE FROM Labels WHERE label_id=3')
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM Tasks'), 6)
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM Task_Categories WHERE category_id=3'), 0)
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM Task_Labels WHERE label_id=3'), 0)

    def test_user_delete_cascades_and_unlinks_other_assignee(self):
        self.db.execute('DELETE FROM Users WHERE user_id=1')
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM Projects WHERE user_id=1'), 0)
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM Tasks WHERE user_id=1'), 0)
        self.assertIsNone(self.scalar('SELECT project_id FROM Tasks WHERE task_id=4'))
        self.assertEqual(self.db.execute('PRAGMA foreign_key_check').fetchall(), [])

    def test_example_queries(self):
        sql = (ROOT / 'database/queries.sql').read_text(encoding='utf-8')
        results = [self.db.execute(statement).fetchall() for statement in sql.split(';') if statement.strip()]
        self.assertEqual([len(r) for r in results], [6, 3, 2, 3])

    def test_indexes(self):
        indexes = {row[0] for row in self.db.execute("SELECT name FROM sqlite_master WHERE type='index'")}
        self.assertTrue({'idx_tasks_user_id', 'idx_tasks_project_id', 'idx_tasks_due_date',
                         'idx_tasks_status', 'idx_projects_user_id',
                         'idx_task_categories_category_id', 'idx_task_labels_label_id'} <= indexes)

    def test_database_creator_preserves_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'sample.db'
            command = [sys.executable, str(ROOT / 'scripts/create_database.py'), str(target)]
            subprocess.run(command, check=True, capture_output=True)
            before = target.read_bytes()
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(target.read_bytes(), before)
            with sqlite3.connect(target) as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM Tasks').fetchone()[0], 6)


if __name__ == '__main__':
    unittest.main()
