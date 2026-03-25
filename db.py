import sqlite3
import os
from datetime import datetime

DB_NAME = "trackora.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            instrument TEXT,
            region TEXT,
            genre TEXT,
            language TEXT,
            current_streak INTEGER DEFAULT 0,
            highest_streak INTEGER DEFAULT 0,
            last_practice_date DATE,
            total_hours REAL DEFAULT 0
        )
    ''')
    
    # Groups table
    c.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            created_at TIMESTAMP
        )
    ''')
    
    # Group members
    c.execute('''
        CREATE TABLE IF NOT EXISTS group_members (
            group_id INTEGER,
            user_id INTEGER,
            joined_at TIMESTAMP,
            PRIMARY KEY (group_id, user_id),
            FOREIGN KEY(group_id) REFERENCES groups(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Practices
    c.execute('''
        CREATE TABLE IF NOT EXISTS practices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            duration_minutes INTEGER,
            created_at TIMESTAMP,
            upvotes INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Collab Requests
    c.execute('''
        CREATE TABLE IF NOT EXISTS collab_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP,
            FOREIGN KEY(sender_id) REFERENCES users(id),
            FOREIGN KEY(receiver_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Helper Functions
def run_query(query, params=(), fetch=True):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(query, params)
    
    if fetch:
        result = c.fetchall()
        conn.close()
        return [dict(row) for row in result]
    else:
        conn.commit()
        lastrowid = c.lastrowid
        conn.close()
        return lastrowid

def get_user_by_username(username):
    res = run_query("SELECT * FROM users WHERE username=?", (username,))
    return res[0] if res else None

def get_user_by_id(user_id):
    res = run_query("SELECT * FROM users WHERE id=?", (user_id,))
    return res[0] if res else None

def create_user(username, password_hash, instrument, region, genre, language):
    query = """
    INSERT INTO users (username, password_hash, instrument, region, genre, language) 
    VALUES (?, ?, ?, ?, ?, ?)
    """
    return run_query(query, (username, password_hash, instrument, region, genre, language), fetch=False)

def update_streak(user_id, duration_minutes):
    user = get_user_by_id(user_id)
    if not user: return False
    
    today = datetime.now().date()
    last_practice = user['last_practice_date']
    
    if last_practice:
        last_practice_date = datetime.strptime(last_practice, '%Y-%m-%d').date()
        delta = (today - last_practice_date).days
        
        if delta == 1:
            new_streak = user['current_streak'] + 1
        elif delta == 0:
            new_streak = user['current_streak'] # Already practiced today
        else:
            new_streak = 1 # Streak broken
    else:
        new_streak = 1

    highest_streak = max(user['highest_streak'], new_streak)
    total_hours = user['total_hours'] + (duration_minutes / 60.0)

    query = """
    UPDATE users 
    SET current_streak = ?, highest_streak = ?, last_practice_date = ?, total_hours = ?
    WHERE id = ?
    """
    run_query(query, (new_streak, highest_streak, today.strftime('%Y-%m-%d'), total_hours, user_id), fetch=False)
    
    # Insert practice record
    practice_query = """
    INSERT INTO practices (user_id, duration_minutes, created_at)
    VALUES (?, ?, ?)
    """
    run_query(practice_query, (user_id, duration_minutes, datetime.now()), fetch=False)
    
    return True

def create_group(name, creator_id):
    try:
        group_id = run_query("INSERT INTO groups (name, created_at) VALUES (?, ?)", (name, datetime.now()), fetch=False)
        run_query("INSERT INTO group_members (group_id, user_id, joined_at) VALUES (?, ?, ?)", (group_id, creator_id, datetime.now()), fetch=False)
        return True
    except sqlite3.IntegrityError:
        return False # Group name exists

def join_group(group_id, user_id):
    try:
        run_query("INSERT INTO group_members (group_id, user_id, joined_at) VALUES (?, ?, ?)", (group_id, user_id, datetime.now()), fetch=False)
        return True
    except:
        return False # Already joined or error
