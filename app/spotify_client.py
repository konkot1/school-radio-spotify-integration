import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import current_app
import os

class SpotifyClient:
    """Klient do komunikacji z Spotify API"""
    
    def __init__(self):
        """Inicjalizuje klienta Spotify z credentials z config"""
        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=current_app.config['SPOTIPY_CLIENT_ID'],
                client_secret=current_app.config['SPOTIPY_CLIENT_SECRET'],
                redirect_uri=current_app.config['SPOTIPY_REDIRECT_URI'],
                scope='playlist-modify-public playlist-modify-private',
                cache_path='.spotify_cache'
            ))
            self.playlist_id = current_app.config['SPOTIFY_PLAYLIST_ID']
        except Exception as e:
            current_app.logger.error(f"Błąd inicjalizacji Spotify: {e}")
            raise
    
    def search_track(self, artist, title):
        """
        Wyszukuje utwór na Spotify po nazwie wykonawcy i tytule.
        
        Returns:
            dict: Informacje o utworze lub None jeśli nie znaleziono
        """
        try:
            query = f"artist:{artist} track:{title}"
            results = self.sp.search(q=query, type='track', limit=1)
            
            if results['tracks']['items']:
                return results['tracks']['items'][0]
            return None
            
        except Exception as e:
            current_app.logger.error(f"Błąd wyszukiwania utworu: {e}")
            return None
    
    def is_track_explicit(self, track):
        """
        Sprawdza czy utwór zawiera treści explicit.
        
        Args:
            track (dict): Obiekt utworu ze Spotify
            
        Returns:
            bool: True jeśli explicit, False w przeciwnym razie
        """
        return track.get('explicit', False)
    
    def add_to_playlist(self, track_uri):
        """
        Dodaje utwór do playlisty.
        
        Args:
            track_uri (str): Spotify URI utworu (spotify:track:...)
            
        Returns:
            bool: True jeśli sukces, False w przeciwnym razie
        """
        try:
            self.sp.playlist_add_items(self.playlist_id, [track_uri])
            current_app.logger.info(f"Dodano utwór {track_uri} do playlisty {self.playlist_id}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Błąd dodawania do playlisty: {e}")
            return False
    
    def get_track_info(self, track):
        """
        Pobiera sformatowane informacje o utworze.
        
        Args:
            track (dict): Obiekt utworu ze Spotify
            
        Returns:
            dict: Sformatowane informacje o utworze
        """
        return {
            'id': track['id'],
            'uri': track['uri'],
            'name': track['name'],
            'artist': ', '.join([artist['name'] for artist in track['artists']]),
            'album': track['album']['name'],
            'url': track['external_urls']['spotify'],
            'album_art': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'duration_ms': track['duration_ms'],
            'explicit': track.get('explicit', False)
        }
