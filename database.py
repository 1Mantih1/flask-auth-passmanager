import sqlite3
from flask import g
from hashlib import sha256
import os
from typing import Dict, List, Optional, Union, Any, cast

DATABASE = os.path.join(os.path.dirname(__file__), 'password_manager.db')

def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def init_db(app):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_passwords_timestamp
            AFTER UPDATE ON passwords
            FOR EACH ROW
            BEGIN
                UPDATE passwords SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
            END
        """)
        
        db.commit()

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def query_db(query: str, args: tuple = (), one: bool = False) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
    db = get_db()
    cur = db.execute(query, args)
    rv = [dict(row) for row in cur.fetchall()]
    cur.close()
    if one:
        return rv[0] if rv else None
    return rv

def add_user(username: str, password: str) -> bool:
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            (username, sha256(password.encode()).hexdigest())
        )
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def verify_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    user = query_db('SELECT * FROM users WHERE username = ?', (username,), one=True)
    if user is None:
        return None
    if isinstance(user, dict) and user.get('password') == sha256(password.encode()).hexdigest():
        return user
    return None

def add_password(user_id: int, name: str, password: str) -> Optional[int]:
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO passwords (user_id, name, password) VALUES (?, ?, ?)',
        (user_id, name, password)
    )
    db.commit()
    return cursor.lastrowid

def get_passwords(user_id: int) -> List[Dict[str, Any]]:
    result = query_db(
        'SELECT * FROM passwords WHERE user_id = ? ORDER BY name',
        (user_id,)
    )
    return cast(List[Dict[str, Any]], result) if result else []

def update_password(password_id: int, new_password: str) -> bool:
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'UPDATE passwords SET password = ? WHERE id = ?',
        (new_password, password_id)
    )
    db.commit()
    return cursor.rowcount > 0

def delete_password(password_id: int) -> bool:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM passwords WHERE id = ?', (password_id,))
    db.commit()
    return cursor.rowcount > 0