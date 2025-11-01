#!/usr/bin/env python3
"""
Script to pre-populate users in the database
"""
import sqlite3
from werkzeug.security import generate_password_hash

# User credentials
USERS = [
    ('mithesh', 'mithesh', 'Mithesh\'s Team'),
    ('susan', 'susan', 'Susan\'s Team'),
    ('minigv', 'minigv', 'Minigv\'s Team'),
    ('suku', 'suku', 'Suku\'s Team'),
    ('hemanth', 'hemanth', 'Hemanth\'s Team'),
    ('thillu', 'thillu', 'Thillu\'s Team'),
    ('ruben', 'ruben', 'Ruben\'s Team'),
    ('keerthi', 'keerthi', 'Keerthi\'s Team'),
    ('aki', 'aki', 'Aki\'s Team'),
    ('leodas', 'leodas', 'Leodas\'s Team'),
    ('bala', 'bala', 'Bala\'s Team'),
]

DATABASE = 'auction.db'

def populate_users():
    """Create database and populate with users"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Create users table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        team_name TEXT,
        purse REAL DEFAULT 100.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Create other tables
    c.execute('''CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        player_name TEXT NOT NULL,
        player_category TEXT,
        purchase_price REAL,
        position INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE(user_id, player_name)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS bids (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        player_name TEXT NOT NULL,
        amount REAL NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_winning INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS auction_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT NOT NULL,
        category TEXT,
        base_price REAL,
        sold_to_user_id INTEGER,
        final_price REAL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sold_to_user_id) REFERENCES users (id)
    )''')
    
    # Insert or update users
    for username, password, team_name in USERS:
        email = f"{username}@auction.local"
        password_hash = generate_password_hash(password)
        
        # Check if user exists
        c.execute('SELECT id FROM users WHERE username = ?', (username,))
        existing = c.fetchone()
        
        if existing:
            # Update existing user
            c.execute('''UPDATE users SET password_hash = ?, team_name = ?, purse = 100.0 
                        WHERE username = ?''', (password_hash, team_name, username))
            print(f"✓ Updated user: {username}")
        else:
            # Insert new user
            c.execute('''INSERT INTO users (username, email, password_hash, team_name, purse) 
                        VALUES (?, ?, ?, ?, ?)''', 
                     (username, email, password_hash, team_name, 100.0))
            print(f"✓ Created user: {username}")
    
    conn.commit()
    conn.close()
    print(f"\n✅ Successfully populated {len(USERS)} users in database!")

if __name__ == '__main__':
    populate_users()

