# database.py
import sqlite3
from datetime import datetime

DB_NAME = "chat.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Table for registered users.
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY
                )''')
    # Table for messages.
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT,
                    recipient TEXT,
                    timestamp TEXT,
                    content TEXT,
                    delivered INTEGER DEFAULT 0
                )''')
    conn.commit()
    conn.close()

def register_user(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users(username) VALUES(?)", (username,))
    conn.commit()
    conn.close()

def store_message(sender, recipient, content):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        "INSERT INTO messages (sender, recipient, timestamp, content, delivered) VALUES (?,?,?,?,0)",
        (sender, recipient, timestamp, content)
    )
    conn.commit()
    conn.close()

def get_offline_messages(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, sender, timestamp, content FROM messages WHERE recipient=? AND delivered=0", (username,))
    messages = c.fetchall()
    conn.close()
    return messages

def mark_messages_delivered(message_ids):
    if not message_ids:
        return
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE messages SET delivered=1 WHERE id IN ({seq})".format(
        seq=','.join(['?']*len(message_ids))
    ), message_ids)
    conn.commit()
    conn.close()

def get_all_registered_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT username FROM users")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]
