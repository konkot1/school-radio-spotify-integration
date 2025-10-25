"""
Moduł do filtrowania wulgaryzmów i nieodpowiednich treści.
"""

# Lista wulgaryzmów (polskie i angielskie)
VULGAR_WORDS = [
    # Polskie
    'kurwa', 'kurwy', 'kurwo', 'kurwą', 'kurwie', 'kurewski',
    'chuj', 'chuja', 'chuju', 'chujem', 'huj',
    'dziwka', 'dziwki', 'dziwko', 'dziwką',
    'pierdol', 'pierdolić', 'pierdoli', 'pierdolę',
    'jebać', 'jebak', 'jebane', 'jebany', 'jebana',
    'dupek', 'dupa', 'dupie', 'dupą', 'dupsko',
    'suka', 'suko', 'suki', 'sukinsyn',
    'skurwysyn', 'skurwiel', 'skurwysynowski',
    'pizda', 'pizdy', 'pizdo', 'pizdą',
    'gówno', 'gowno', 'gówna',
    'spierdalaj', 'spierdala', 'spierdalać',
    'zajebisty', 'zajebiste', 'zajebista',
    'kutas', 'kutasa', 'kutasie',
    'cipka', 'cipa',
    'srać', 'sraka',
    'pierdzieć', 'pierdnąć',
    
    # Angielskie
    'fuck', 'fucking', 'fucker', 'fucked', 'fucks',
    'shit', 'shitty', 'shithead',
    'bitch', 'bitches', 'bitching',
    'ass', 'asshole', 'asses',
    'damn', 'damned', 'damnit',
    'cunt', 'cunts',
    'dick', 'dickhead', 'dicks',
    'pussy', 'pussies',
    'bastard', 'bastards',
    'whore', 'whores',
    'slut', 'sluts', 'slutty',
    'cock', 'cocks',
    'piss', 'pissed', 'pissing',
    'motherfucker', 'motherfucking',
    'bullshit',
    'nigga', 'nigger',
    'retard', 'retarded',
]

def contains_vulgar_words(text):
    """
    Sprawdza czy tekst zawiera wulgaryzmy.
    
    Args:
        text: Tekst do sprawdzenia
    
    Returns:
        True jeśli znaleziono wulgaryzmy, False w przeciwnym razie
    """
    if not text:
        return False
    
    # Zamień na małe litery dla porównania
    text_lower = text.lower()
    
    # Sprawdź każde słowo z listy
    for word in VULGAR_WORDS:
        # Sprawdź czy słowo występuje jako całe słowo (nie część innego słowa)
        # Używamy word boundaries (\b) w regex
        import re
        pattern = r'\b' + re.escape(word) + r'\b'
        if re.search(pattern, text_lower):
            return True
    
    return False

def is_content_appropriate(artist, title):
    """
    Sprawdza czy treść (wykonawca i tytuł) jest odpowiednia.
    
    Args:
        artist: Nazwa wykonawcy
        title: Tytuł piosenki
    
    Returns:
        Tuple (is_ok: bool, reason: str)
        - is_ok: True jeśli treść jest OK, False jeśli nie
        - reason: Powód odrzucenia (jeśli is_ok=False)
    """
    # Sprawdź nazwę wykonawcy
    if contains_vulgar_words(artist):
        return False, "Wulgaryzmy w nazwie wykonawcy"
    
    # Sprawdź tytuł
    if contains_vulgar_words(title):
        return False, "Wulgaryzmy w tytule piosenki"
    
    return True, "OK"