from flask import Flask
from app.config import Config
from app.database import init_db, close_db

def create_app():
    """
    Factory function do tworzenia aplikacji Flask.
    Inicjalizuje konfigurację, bazę danych i rejestruje routes.
    """
    app = Flask(__name__, static_folder='../static', template_folder='templates')
    
    # Załaduj konfigurację
    app.config.from_object(Config)
    
    # Waliduj konfigurację
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ BŁĄD KONFIGURACJI: {e}")
        print("💡 Upewnij się, że plik .env jest poprawnie skonfigurowany")
        exit(1)
    
    # Inicjalizuj bazę danych
    with app.app_context():
        init_db()
    
    # Rejestruj zamykanie połączenia z bazą przy końcu requestu
    app.teardown_appcontext(close_db)
    
    # Zarejestruj routes
    from app.routes import bp
    app.register_blueprint(bp)
    
    return app
