import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Konfiguracja aplikacji Flask"""
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Spotify API
    SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
    SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
    SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
    SPOTIFY_PLAYLIST_ID = os.getenv('SPOTIFY_PLAYLIST_ID')
    
    # Limity zgłoszeń
    MAX_SONGS_PER_PERIOD = int(os.getenv('MAX_SONGS_PER_PERIOD', 1))
    LIMIT_PERIOD_DAYS = int(os.getenv('LIMIT_PERIOD_DAYS', 2))
    
    # Email
    SCHOOL_EMAIL_DOMAIN = os.getenv('SCHOOL_EMAIL_DOMAIN', 'zspbytow.pl')
    
    # Email SMTP configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL')
    SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'Radiowęzeł ZSP Bytów')
    
    # Admini (bez limitu zgłoszeń)
    ADMIN_EMAILS = [email.strip().lower() for email in os.getenv('ADMIN_EMAILS', '').split(',') if email.strip()]
    
    # Baza danych
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/submissions.db')
    
    @staticmethod
    def validate():
        """Waliduje czy wszystkie wymagane zmienne środowiskowe są ustawione"""
        required = [
            'SPOTIPY_CLIENT_ID',
            'SPOTIPY_CLIENT_SECRET',
            'SPOTIPY_REDIRECT_URI',
            'SPOTIFY_PLAYLIST_ID'
        ]
        
        missing = [key for key in required if not os.getenv(key)]
        
        if missing:
            raise ValueError(f"Brakujące zmienne środowiskowe: {', '.join(missing)}")
    
    @staticmethod
    def is_admin(email):
        """Sprawdza czy email jest na liście adminów"""
        return email.lower() in Config.ADMIN_EMAILS
