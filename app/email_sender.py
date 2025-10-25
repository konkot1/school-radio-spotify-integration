import random
import string

def generate_verification_code():
    """Generuje 6-cyfrowy kod weryfikacyjny"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email, code):
    """
    Wysyła email z kodem weryfikacyjnym.
    
    W wersji deweloperskiej - wyświetla w konsoli.
    W produkcji - użyj SMTP lub API (np. SendGrid, Mailgun).
    """
    print("\n" + "="*60)
    print("📧 WYSŁANO EMAIL WERYFIKACYJNY")
    print("="*60)
    print(f"Do: {email}")
    print(f"Temat: Kod weryfikacyjny - Radiowęzeł ZSP Bytów")
    print(f"\nTwój kod weryfikacyjny: {code}")
    print(f"\nKod jest ważny przez 10 minut.")
    print("="*60 + "\n")
    
    # TODO: W produkcji zamień na prawdziwe wysyłanie emaili
    return True
