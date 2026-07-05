import sqlite3


def get_db():
    conn = sqlite3.connect('users.db')
    return conn


def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, salt TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS passwords (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, site_name TEXT, saved_password TEXT)')
    # Databases created before encryption was added are missing the salt column.
    columns = [row[1] for row in conn.execute('PRAGMA table_info(users)')]
    if 'salt' not in columns:
        conn.execute('ALTER TABLE users ADD COLUMN salt TEXT')
    conn.commit()
    conn.close()
