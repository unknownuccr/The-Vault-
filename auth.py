import bcrypt

from database import get_db
from crypto import new_salt


# hashes a password into bcrypt format
def hashing_a_pass(user_password):
    password_bytes = user_password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode('utf-8')


# checks a password
def check_pass(entered_pass, hashed_password):
    attempt_bytes = entered_pass.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(attempt_bytes, hash_bytes)


# adds a new account to the users table
def add_to_db(username, hashed_password):
    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO users (username, password, salt) VALUES (?, ?, ?)',
            (username, hashed_password, new_salt()),
        )
        conn.commit()
    finally:
        conn.close()


def get_user(username):
    conn = get_db()
    row = conn.execute('SELECT password FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return row[0] if row else None


def get_user_salt(username):
    """Return the user's KDF salt, creating one for accounts that predate encryption."""
    conn = get_db()
    try:
        row = conn.execute('SELECT salt FROM users WHERE username = ?', (username,)).fetchone()
        if row is None:
            return None
        if row[0]:
            return row[0]
        salt = new_salt()
        conn.execute('UPDATE users SET salt = ? WHERE username = ?', (salt, username))
        conn.commit()
        return salt
    finally:
        conn.close()


def save_password(username, site_name, saved_password):
    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO passwords (username, site_name, saved_password) VALUES (?, ?, ?)',
            (username, site_name, saved_password),
        )
        conn.commit()
    finally:
        conn.close()


def get_passwords(username):
    conn = get_db()
    rows = conn.execute(
        'SELECT site_name, saved_password, id FROM passwords WHERE username = ? ORDER BY site_name COLLATE NOCASE',
        (username,),
    ).fetchall()
    conn.close()
    return rows


def count_passwords(username):
    conn = get_db()
    row = conn.execute('SELECT COUNT(*) FROM passwords WHERE username = ?', (username,)).fetchone()
    conn.close()
    return row[0]


def update_password_value(entry_id, username, new_value):
    conn = get_db()
    try:
        conn.execute(
            'UPDATE passwords SET saved_password = ? WHERE id = ? AND username = ?',
            (new_value, entry_id, username),
        )
        conn.commit()
    finally:
        conn.close()


def delete_password(entry_id, username):
    """Delete an entry, but only if it belongs to this user."""
    conn = get_db()
    try:
        cur = conn.execute(
            'DELETE FROM passwords WHERE id = ? AND username = ?',
            (entry_id, username),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
