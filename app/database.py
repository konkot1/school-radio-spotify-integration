import sqlite3
from flask import g
from datetime import datetime, timedelta
import os

DATABASE_PATH = 'data/submissions.db'

def get_db():
    """Pobiera połączenie z bazą danych"""
    if 'db' not in g:
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        g.db = sqlite3.connect(DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Zamyka połączenie z bazą danych"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Inicjalizuje bazę danych"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            email_hash TEXT NOT NULL,
            artist TEXT NOT NULL,
            title TEXT NOT NULL,
            spotify_track_id TEXT,
            spotify_track_uri TEXT,
            status TEXT NOT NULL CHECK(status IN ('approved', 'rejected', 'pending')),
            rejection_reason TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            verified BOOLEAN DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verification_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            code TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_email_hash ON submissions(email_hash)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_submitted_at ON submissions(submitted_at)
    ''')
    
    db.commit()

def save_submission(email, email_hash, artist, title, spotify_track_id, 
                   spotify_track_uri, status, rejection_reason=None):
    """Zapisuje zgłoszenie do bazy"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        INSERT INTO submissions 
        (email, email_hash, artist, title, spotify_track_id, spotify_track_uri, status, rejection_reason, verified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
    ''', (email, email_hash, artist, title, spotify_track_id, spotify_track_uri, status, rejection_reason))
    
    db.commit()
    return cursor.lastrowid

def count_user_submissions_in_period(email_hash, days=2):
    """Liczy zgłoszenia użytkownika w ostatnich N dniach"""
    db = get_db()
    cursor = db.cursor()
    
    period_start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        SELECT COUNT(*) FROM submissions
        WHERE email_hash = ? AND submitted_at >= ? AND status = 'approved'
    ''', (email_hash, period_start))
    
    return cursor.fetchone()[0]

def get_submissions_today():
    """Pobiera wszystkie zgłoszenia z dzisiaj"""
    db = get_db()
    cursor = db.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute('''
        SELECT * FROM submissions
        WHERE DATE(submitted_at) = ?
        ORDER BY submitted_at DESC
    ''', (today,))
    
    return [dict(row) for row in cursor.fetchall()]

def get_all_submissions(limit=100):
    """Pobiera wszystkie zgłoszenia (dla panelu admin)"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT * FROM submissions
        ORDER BY submitted_at DESC
        LIMIT ?
    ''', (limit,))
    
    return [dict(row) for row in cursor.fetchall()]

def save_verification_code(email, code, expires_minutes=10):
    """Zapisuje kod weryfikacyjny"""
    db = get_db()
    cursor = db.cursor()
    
    expires_at = (datetime.now() + timedelta(minutes=expires_minutes)).strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        INSERT INTO verification_codes (email, code, expires_at)
        VALUES (?, ?, ?)
    ''', (email, code, expires_at))
    
    db.commit()

def verify_code(email, code):
    """Weryfikuje kod"""
    db = get_db()
    cursor = db.cursor()
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        SELECT * FROM verification_codes
        WHERE email = ? AND code = ? AND expires_at > ? AND used = 0
        ORDER BY created_at DESC
        LIMIT 1
    ''', (email, code, now))
    
    result = cursor.fetchone()
    
    if result:
        # Oznacz kod jako użyty
        cursor.execute('''
            UPDATE verification_codes
            SET used = 1
            WHERE id = ?
        ''', (result['id'],))
        db.commit()
        return True
    
    return False
