import sqlite3
from flask import g
from hashlib import sha256

DATABASE = 'password_manager.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS passwords (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        password TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id))''')
    db.commit()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def add_user(username, password):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, sha256(password.encode()).hexdigest()))
    db.commit()

def verify_user(username, password):
    user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
    if user and user[2] == sha256(password.encode()).hexdigest():
        return user
    return None

def add_password(user_id, name, password):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO passwords (user_id, name, password) VALUES (?, ?, ?)', (user_id, name, password))
    db.commit()

def get_passwords(user_id):
    return query_db('SELECT * FROM passwords WHERE user_id = ?', [user_id])

def update_password(id, new_password):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE passwords SET password = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (new_password, id))
    db.commit()

def delete_password(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM passwords WHERE id = ?', (id,))
    db.commit()
