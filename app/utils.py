import hashlib
import re
from flask import current_app

def hash_email(email):
    """Hashuje email dla prywatności (SHA256)"""
    return hashlib.sha256(email.lower().encode()).hexdigest()

def validate_school_email(email):
    """Sprawdza czy email jest z domeny szkolnej"""
    domain = current_app.config.get('SCHOOL_EMAIL_DOMAIN', 'zspbytow.pl')
    pattern = rf'^[a-zA-Z0-9._%+-]+@{re.escape(domain)}$'
    return bool(re.match(pattern, email.lower()))

def sanitize_input(text):
    """Oczyszcza input użytkownika"""
    if not text:
        return ''
    return text.strip()[:200]  # Max 200 znaków
