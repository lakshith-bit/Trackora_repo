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
            name TEXT,
            email TEXT UNIQUE,
            age INTEGER,
            instrument TEXT,
            region TEXT,
            genre TEXT,
            language TEXT,
            experience TEXT,
            teacher TEXT,
            is_public BOOLEAN DEFAULT 1,
            profile_points INTEGER DEFAULT 0,
            target_bpm INTEGER DEFAULT 85,
            current_bpm INTEGER DEFAULT 70,
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
    
    # Tasks
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_tasks (
            user_id INTEGER,
            task_date DATE,
            task_desc TEXT,
            completed BOOLEAN DEFAULT 0,
            PRIMARY KEY (user_id, task_date)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS group_daily_tasks (
            group_id INTEGER,
            task_date DATE,
            task_desc TEXT,
            PRIMARY KEY (group_id, task_date)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS group_task_completions (
            group_id INTEGER,
            user_id INTEGER,
            task_date DATE,
            PRIMARY KEY (group_id, user_id, task_date)
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

def create_user(username, password_hash, name, email, age, instrument, region, genre, language, experience, teacher, is_public):
    query = """
    INSERT INTO users (username, password_hash, name, email, age, instrument, region, genre, language, experience, teacher, is_public) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    return run_query(query, (username, password_hash, name, email, age, instrument, region, genre, language, experience, teacher, is_public), fetch=False)

def update_profile_points(user_id, points):
    query = "UPDATE users SET profile_points = profile_points + ? WHERE id = ?"
    run_query(query, (points, user_id), fetch=False)

def update_user_bpm(user_id, new_bpm):
    query = "UPDATE users SET current_bpm = ? WHERE id = ?"
    run_query(query, (new_bpm, user_id), fetch=False)

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
        
def get_or_create_daily_task(user_id):
    import random
    today = datetime.now().strftime('%Y-%m-%d')
    res = run_query("SELECT * FROM daily_tasks WHERE user_id = ? AND task_date = ?", (user_id, today))
    if res:
        return res[0]
    
    tasks = ["Practice scales for 15 mins", "Upload a new recording", "Play a new piece", "Review a collaboration request"]
    desc = random.choice(tasks)
    run_query("INSERT INTO daily_tasks (user_id, task_date, task_desc, completed) VALUES (?, ?, ?, 0)", (user_id, today, desc), fetch=False)
    return {"user_id": user_id, "task_date": today, "task_desc": desc, "completed": 0}

def complete_daily_task(user_id):
    today = datetime.now().strftime('%Y-%m-%d')
    run_query("UPDATE daily_tasks SET completed = 1 WHERE user_id = ? AND task_date = ?", (user_id, today), fetch=False)
    # Give them a 1 min practice entry to trigger streak update logic easily
    update_streak(user_id, 1)

def get_or_create_group_task(group_id):
    import random
    today = datetime.now().strftime('%Y-%m-%d')
    res = run_query("SELECT * FROM group_daily_tasks WHERE group_id = ? AND task_date = ?", (group_id, today))
    if res:
        return res[0]
    
    tasks = ["All members must upload a recording", "All members must uphold their streaks", "All members must play a piece"]
    desc = random.choice(tasks)
    run_query("INSERT INTO group_daily_tasks (group_id, task_date, task_desc) VALUES (?, ?, ?)", (group_id, today, desc), fetch=False)
    return {"group_id": group_id, "task_date": today, "task_desc": desc}

def complete_group_task_for_user(group_id, user_id):
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        run_query("INSERT INTO group_task_completions (group_id, user_id, task_date) VALUES (?, ?, ?)", (group_id, user_id, today), fetch=False)
        return True
    except sqlite3.IntegrityError:
        return False

def get_group_completion_status(group_id):
    today = datetime.now().strftime('%Y-%m-%d')
    members = run_query("SELECT user_id FROM group_members WHERE group_id = ?", (group_id,))
    completions = run_query("SELECT user_id FROM group_task_completions WHERE group_id = ? AND task_date = ?", (group_id, today))
    
    member_ids = {m['user_id'] for m in members}
    completed_ids = {c['user_id'] for c in completions}
    
    return {
        "total_members": len(member_ids),
        "completed": len(completed_ids),
        "all_done": len(member_ids) > 0 and member_ids == completed_ids
    }

def complete_all_group_tasks_for_user(user_id):
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    groups = run_query("SELECT group_id FROM group_members WHERE user_id = ?", (user_id,))
    if groups:
        for g in groups:
            done = run_query("SELECT id FROM group_task_completions WHERE group_id = ? AND user_id = ? AND task_date = ?", (g['group_id'], user_id, today))
            if not done:
                run_query("INSERT INTO group_task_completions (group_id, user_id, task_date) VALUES (?, ?, ?)", (g['group_id'], user_id, today), fetch=False)
