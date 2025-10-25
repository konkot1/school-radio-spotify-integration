from flask import Blueprint, render_template, request, jsonify, current_app
from app.database import (
    save_submission,
    count_user_submissions_in_period,
    get_submissions_today,
    get_all_submissions,
    save_verification_code,
    verify_code
)
from app.spotify_client import SpotifyClient
from app.content_filter import is_content_appropriate
from app.utils import hash_email, validate_school_email, sanitize_input
from app.email_sender import generate_verification_code, send_verification_email
from app.config import Config

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Strona główna z formularzem zgłoszenia"""
    return render_template('index.html')

@bp.route('/admin')
def admin():
    """Panel administracyjny - lista zgłoszeń"""
    submissions = get_all_submissions(limit=200)
    today_submissions = get_submissions_today()

    return render_template(
        'admin.html',
        submissions=submissions,
        today_count=len(today_submissions)
    )

@bp.route('/api/request-code', methods=['POST'])
def request_verification_code():
    """Wysyła kod weryfikacyjny na email"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not validate_school_email(email):
            return jsonify({
                'success': False,
                'message': f'Tylko emaile @{current_app.config["SCHOOL_EMAIL_DOMAIN"]} są akceptowane'
            }), 400
        
        # Generuj kod
        code = generate_verification_code()
        
        # Zapisz w bazie
        save_verification_code(email, code, expires_minutes=10)
        
        # Wyślij email
        send_verification_email(email, code)
        
        return jsonify({
            'success': True,
            'message': f'Kod weryfikacyjny został wysłany na {email}'
        })
        
    except Exception as e:
        current_app.logger.error(f"Błąd w /api/request-code: {e}")
        return jsonify({
            'success': False,
            'message': 'Wystąpił błąd. Spróbuj ponownie.'
        }), 500

@bp.route('/api/submit', methods=['POST'])
def submit_song():
    """Endpoint do zgłaszania piosenek (z weryfikacją kodu)"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'message': 'Brak danych w requeście'
            }), 400

        email = data.get('email', '').strip().lower()
        verification_code = data.get('code', '').strip()
        artist = sanitize_input(data.get('artist', ''))
        title = sanitize_input(data.get('title', ''))

        # Walidacja
        if not email or not artist or not title or not verification_code:
            return jsonify({
                'success': False,
                'message': 'Wszystkie pola są wymagane'
            }), 400

        # Sprawdź email
        if not validate_school_email(email):
            return jsonify({
                'success': False,
                'message': f'Tylko emaile @{current_app.config["SCHOOL_EMAIL_DOMAIN"]} są akceptowane'
            }), 400

        # Weryfikuj kod
        if not verify_code(email, verification_code):
            return jsonify({
                'success': False,
                'message': 'Nieprawidłowy lub wygasły kod weryfikacyjny'
            }), 400

        email_hash = hash_email(email)

        # Sprawdź limit - admini bez limitu
        if Config.is_admin(email):
            print(f"👑 Admin {email} - pominięto limit zgłoszeń")
        else:
            limit_days = current_app.config.get('LIMIT_PERIOD_DAYS', 2)
            max_songs = current_app.config.get('MAX_SONGS_PER_PERIOD', 1)
            period_count = count_user_submissions_in_period(email_hash, days=limit_days)

            if period_count >= max_songs:
                return jsonify({
                    'success': False,
                    'message': f'Możesz zgłosić maksymalnie {max_songs} piosenkę na {limit_days} dni. Spróbuj ponownie później!'
                }), 429

        # Sprawdź wulgaryzmy
        is_ok, reason = is_content_appropriate(artist, title)
        if not is_ok:
            save_submission(
                email=email,
                email_hash=email_hash,
                artist=artist,
                title=title,
                spotify_track_id=None,
                spotify_track_uri=None,
                status='rejected',
                rejection_reason=reason
            )

            return jsonify({
                'success': False,
                'message': f'Zgłoszenie odrzucone: {reason}'
            }), 400

        # Wyszukaj na Spotify
        spotify = SpotifyClient()
        track = spotify.search_track(artist, title)

        if not track:
            save_submission(
                email=email,
                email_hash=email_hash,
                artist=artist,
                title=title,
                spotify_track_id=None,
                spotify_track_uri=None,
                status='rejected',
                rejection_reason='Nie znaleziono utworu na Spotify'
            )

            return jsonify({
                'success': False,
                'message': 'Nie znaleziono utworu na Spotify. Sprawdź poprawność nazwy wykonawcy i tytułu.'
            }), 404

        # Sprawdź explicit
        if spotify.is_track_explicit(track):
            save_submission(
                email=email,
                email_hash=email_hash,
                artist=artist,
                title=title,
                spotify_track_id=track['id'],
                spotify_track_uri=track['uri'],
                status='rejected',
                rejection_reason='Utwór zawiera treści explicit'
            )

            return jsonify({
                'success': False,
                'message': 'Utwór zawiera treści explicit i nie może być dodany'
            }), 400

        # Dodaj do playlisty
        success = spotify.add_to_playlist(track['uri'])

        if not success:
            return jsonify({
                'success': False,
                'message': 'Błąd podczas dodawania do playlisty. Spróbuj ponownie później.'
            }), 500

        # Zapisz
        track_info = spotify.get_track_info(track)
        save_submission(
            email=email,
            email_hash=email_hash,
            artist=track_info['artist'],
            title=track_info['name'],
            spotify_track_id=track_info['id'],
            spotify_track_uri=track_info['uri'],
            status='approved',
            rejection_reason=None
        )

        return jsonify({
            'success': True,
            'message': '✅ Piosenka została pomyślnie dodana do playlisty! 🎵',
            'track': {
                'artist': track_info['artist'],
                'title': track_info['name'],
                'url': track_info['url'],
                'album_art': track_info.get('album_art'),
                'duration': track_info.get('duration_ms')
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Błąd w /api/submit: {e}")
        return jsonify({
            'success': False,
            'message': 'Wystąpił nieoczekiwany błąd. Spróbuj ponownie później.'
        }), 500

@bp.route('/api/stats')
def get_stats():
    """Endpoint zwracający statystyki"""
    try:
        today_submissions = get_submissions_today()

        approved = len([s for s in today_submissions if s['status'] == 'approved'])
        rejected = len([s for s in today_submissions if s['status'] == 'rejected'])

        return jsonify({
            'success': True,
            'today_total': len(today_submissions),
            'today_approved': approved,
            'today_rejected': rejected
        })

    except Exception as e:
        current_app.logger.error(f"Błąd w /api/stats: {e}")
        return jsonify({
            'success': False,
            'message': 'Błąd pobierania statystyk'
        }), 500

# Aliasy dla kompatybilności
@bp.route('/submit', methods=['POST'])
def submit_song_alias():
    return submit_song()

@bp.route('/stats')
def get_stats_alias():
    return get_stats()

@bp.route('/request-code', methods=['POST'])
def request_code_alias():
    return request_verification_code()
