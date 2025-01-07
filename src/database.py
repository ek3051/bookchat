#!/usr/bin/env python3

import sqlite3
import os
from datetime import datetime

def get_db_connection():
    """Create a database connection and return the connection object."""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'bookchat.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with the schema."""
    conn = get_db_connection()
    try:
        # Read schema file
        schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'schema.sql')
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        # Execute schema
        conn.executescript(schema)
        conn.commit()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def add_user(github_id, username, avatar_url):
    """Add a new user to the database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (github_id, username, avatar_url)
            VALUES (?, ?, ?)
        ''', (github_id, username, avatar_url))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_user_by_github_id(github_id):
    """Get user information by GitHub ID."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE github_id = ?', (github_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def add_message(user_id, content):
    """Add a new message to the database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        now = datetime.utcnow()
        cursor.execute('''
            INSERT INTO messages (user_id, content, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, content, now, now))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_messages(limit=50, offset=0):
    """Get messages with user information."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.*, u.username, u.avatar_url
            FROM messages m
            JOIN users u ON m.user_id = u.id
            ORDER BY m.created_at DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        return cursor.fetchall()
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
