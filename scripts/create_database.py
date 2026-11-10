"""Create a fresh sample database without overwriting an existing file."""
import argparse
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, nargs='?', default=ROOT / 'tasks.db')
    args = parser.parse_args()
    # Exclusive creation protects existing data, including an empty database.
    with args.output.open('xb'):
        pass
    try:
        with sqlite3.connect(args.output) as connection:
            for filename in ('schema.sql', 'seed_data.sql'):
                connection.executescript((ROOT / 'database' / filename).read_text(encoding='utf-8'))
            if connection.execute('PRAGMA foreign_key_check').fetchall():
                raise RuntimeError('Foreign key check failed')
            if connection.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise RuntimeError('Integrity check failed')
        print(f'Created: {args.output.resolve()}')
    except BaseException:
        args.output.unlink(missing_ok=True)
        raise


if __name__ == '__main__':
    main()
