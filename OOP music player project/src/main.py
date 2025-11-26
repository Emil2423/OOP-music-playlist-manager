"""Main CLI application for music playlist manager.

Provides an interactive command-line interface for demonstrating CRUD operations
on Song, User, and Playlist entities. Integrates Student A's model classes with
Student B's repository layer.
"""

import sys
import os

import logging
from logging_config import setup_logging, get_logger
from database.connection import DatabaseConnection
from database.schema import initialize_database
from models.song import Song
from models.user import User
from models.playlist import Playlist
from repositories.song_repository import SongRepository
from repositories.user_repository import UserRepository
from repositories.playlist_repository import PlaylistRepository
from services.track_factory import TrackFactory

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Global repositories
song_repo = None
user_repo = None
playlist_repo = None


def initialize_app():
    """Initialize application - setup database and repositories.
    
    Raises:
        RuntimeError: If initialization fails
    """
    global song_repo, user_repo, playlist_repo
    
    try:
        logger.info("=" * 60)
        logger.info("Initializing Music Playlist Manager Application")
        logger.info("=" * 60)
        
        # Connect to database
        db = DatabaseConnection()
        db.connect()
        logger.info("Database connection established")
        
        # Database schema initialization skipped as per user requirement
        # initialize_database(db)
        # logger.info("Database schema initialized")
        
        # Initialize repositories
        song_repo = SongRepository(db)
        user_repo = UserRepository(db)
        playlist_repo = PlaylistRepository(db)
        logger.info("All repositories initialized")
        
        logger.info("Application initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Application initialization failed: {e}")
        raise


def shutdown_app():
    """Shutdown application - close database connection.
    
    Note:
        Safe to call even if not fully initialized.
    """
    try:
        db = DatabaseConnection()
        db.disconnect()
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


def display_menu():
    """Display main CLI menu."""
    print("\n" + "=" * 60)
    print("Music Playlist Manager - Sprint 1 CLI")
    print("=" * 60)
    print("\nOperations:")
    print("  1. Create Song")
    print("  2. View All Songs")
    print("  3. Search Song by Artist")
    print("  4. Search Song by Genre")
    print("  5. Create User")
    print("  6. View All Users")
    print("  7. Find User by Username")
    print("  8. Create Playlist")
    print("  9. View All Playlists")
    print(" 10. View User's Playlists")
    print(" 11. Add Song to Playlist")
    print(" 12. View Playlist Songs")
    print("  0. Exit")
    print("-" * 60)


def create_song():
    """Create a new song (demonstrates CREATE operation)."""
    try:
        print("\n--- Create New Song ---")
        title = input("Song title: ").strip()
        if not title:
            print("❌ Title cannot be empty")
            return
        
        artist = input("Artist name: ").strip()
        if not artist:
            print("❌ Artist cannot be empty")
            return
        
        genre = input("Genre: ").strip()
        if not genre:
            print("❌ Genre cannot be empty")
            return
        
        try:
            duration = int(input("Duration (seconds): ").strip())
            if duration <= 0:
                print("❌ Duration must be positive")
                return
        except ValueError:
            print("❌ Duration must be a number")
            return
        
        # Create Song using TrackFactory (Factory Pattern)
        song = TrackFactory.create_song(title, duration, artist, genre)
        
        # Persist using Student B's repository
        song_id = song_repo.create(song)
        print(f"✓ Song created successfully (ID: {song_id})")
        
    except Exception as e:
        logger.error(f"Failed to create song: {e}")
        print(f"❌ Error: {e}")


def view_all_songs():
    """View all songs in database (demonstrates READ operation)."""
    try:
        print("\n--- All Songs ---")
        songs = song_repo.read_all()
        
        if not songs:
            print("No songs in database")
            return
        
        print(f"\nTotal songs: {len(songs)}\n")
        for i, song in enumerate(songs, 1):
            print(f"{i}. {song.title}")
            print(f"   Artist: {song.artist} | Genre: {song.genre} | Duration: {song.duration}s")
        
    except Exception as e:
        logger.error(f"Failed to view songs: {e}")
        print(f"❌ Error: {e}")


def search_songs_by_artist():
    """Search songs by artist (demonstrates READ with filter)."""
    try:
        print("\n--- Search Songs by Artist ---")
        artist = input("Enter artist name: ").strip()
        
        if not artist:
            print("❌ Artist name cannot be empty")
            return
        
        songs = song_repo.read_by_artist(artist)
        
        if not songs:
            print(f"No songs found by artist: {artist}")
            return
        
        print(f"\nSongs by {artist} ({len(songs)} total):\n")
        for i, song in enumerate(songs, 1):
            print(f"{i}. {song.title}")
            print(f"   Genre: {song.genre} | Duration: {song.duration}s")
        
    except Exception as e:
        logger.error(f"Failed to search songs: {e}")
        print(f"❌ Error: {e}")


def search_songs_by_genre():
    """Search songs by genre (demonstrates READ with filter)."""
    try:
        print("\n--- Search Songs by Genre ---")
        genre = input("Enter genre: ").strip()
        
        if not genre:
            print("❌ Genre cannot be empty")
            return
        
        songs = song_repo.read_by_genre(genre)
        
        if not songs:
            print(f"No songs found in genre: {genre}")
            return
        
        print(f"\nSongs in {genre} ({len(songs)} total):\n")
        for i, song in enumerate(songs, 1):
            print(f"{i}. {song.title}")
            print(f"   Artist: {song.artist} | Duration: {song.duration}s")
        
    except Exception as e:
        logger.error(f"Failed to search songs: {e}")
        print(f"❌ Error: {e}")


def create_user():
    """Create a new user (demonstrates CREATE operation)."""
    try:
        print("\n--- Create New User ---")
        username = input("Username: ").strip()
        if not username:
            print("❌ Username cannot be empty")
            return
        
        email = input("Email: ").strip()
        if not email or '@' not in email:
            print("❌ Valid email required")
            return
        
        # Create User using Student A's model
        user = User(
            username=username,
            email=email
        )
        
        # Persist using Student B's repository
        user_id = user_repo.create(user)
        print(f"✓ User created successfully (ID: {user_id})")
        
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        print(f"❌ Error: {e}")


def view_all_users():
    """View all users in database (demonstrates READ operation)."""
    try:
        print("\n--- All Users ---")
        users = user_repo.read_all()
        
        if not users:
            print("No users in database")
            return
        
        print(f"\nTotal users: {len(users)}\n")
        for i, user in enumerate(users, 1):
            username = user._User__username
            email = user._User__email
            print(f"{i}. {username}")
            print(f"   Email: {email} | ID: {user.id}")
        
    except Exception as e:
        logger.error(f"Failed to view users: {e}")
        print(f"❌ Error: {e}")


def find_user_by_username():
    """Find user by username (demonstrates READ with filter)."""
    try:
        print("\n--- Find User by Username ---")
        username = input("Enter username: ").strip()
        
        if not username:
            print("❌ Username cannot be empty")
            return
        
        user = user_repo.read_by_username(username)
        
        if not user:
            print(f"No user found with username: {username}")
            return
        
        email = user._User__email
        print(f"\nUser found:")
        print(f"  Username: {username}")
        print(f"  Email: {email}")
        print(f"  ID: {user.id}")
        
    except Exception as e:
        logger.error(f"Failed to find user: {e}")
        print(f"❌ Error: {e}")


def create_playlist():
    """Create a new playlist (demonstrates CREATE operation)."""
    try:
        print("\n--- Create New Playlist ---")
        name = input("Playlist name: ").strip()
        if not name:
            print("❌ Playlist name cannot be empty")
            return
        
        print("\nSelect owner (user):")
        users = user_repo.read_all()
        
        if not users:
            print("❌ No users in database. Create a user first.")
            return
        
        for i, user in enumerate(users, 1):
            username = user._User__username
            print(f"  {i}. {username} (ID: {user.id})")
        
        try:
            choice = int(input("Select user number: ").strip())
            if choice < 1 or choice > len(users):
                print("❌ Invalid selection")
                return
            owner_id = users[choice - 1].id
        except ValueError:
            print("❌ Invalid input")
            return
        
        # Create Playlist using Student A's model
        playlist = Playlist(
            name=name,
            owner_id=owner_id
        )
        
        # Persist using Student B's repository
        playlist_id = playlist_repo.create(playlist)
        print(f"✓ Playlist created successfully (ID: {playlist_id})")
        
    except Exception as e:
        logger.error(f"Failed to create playlist: {e}")
        print(f"❌ Error: {e}")


def view_all_playlists():
    """View all playlists in database (demonstrates READ operation)."""
    try:
        print("\n--- All Playlists ---")
        playlists = playlist_repo.read_all()
        
        if not playlists:
            print("No playlists in database")
            return
        
        print(f"\nTotal playlists: {len(playlists)}\n")
        for i, playlist in enumerate(playlists, 1):
            owner = user_repo.read_by_id(playlist.owner_id)
            owner_name = owner._User__username if owner else "Unknown"
            print(f"{i}. {playlist.name}")
            print(f"   Owner: {owner_name} | ID: {playlist.id}")
        
    except Exception as e:
        logger.error(f"Failed to view playlists: {e}")
        print(f"❌ Error: {e}")


def view_user_playlists():
    """View playlists owned by a user (demonstrates READ with filter)."""
    try:
        print("\n--- View User's Playlists ---")
        username = input("Enter username: ").strip()
        
        if not username:
            print("❌ Username cannot be empty")
            return
        
        user = user_repo.read_by_username(username)
        if not user:
            print(f"No user found with username: {username}")
            return
        
        playlists = playlist_repo.read_by_owner_id(user.id)
        
        if not playlists:
            print(f"No playlists for user: {username}")
            return
        
        print(f"\nPlaylists for {username} ({len(playlists)} total):\n")
        for i, playlist in enumerate(playlists, 1):
            num_songs = len(playlist_repo.get_playlist_songs(playlist.id))
            print(f"{i}. {playlist.name}")
            print(f"   Songs: {num_songs} | ID: {playlist.id}")
        
    except Exception as e:
        logger.error(f"Failed to view playlists: {e}")
        print(f"❌ Error: {e}")


def add_song_to_playlist():
    """Add song to playlist (demonstrates CREATE for junction table)."""
    try:
        print("\n--- Add Song to Playlist ---")
        
        songs = song_repo.read_all()
        if not songs:
            print("❌ No songs in database")
            return
        
        playlists = playlist_repo.read_all()
        if not playlists:
            print("❌ No playlists in database")
            return
        
        print("\nSelect song:")
        for i, song in enumerate(songs, 1):
            print(f"  {i}. {song.title} by {song.artist}")
        
        try:
            song_choice = int(input("Select song number: ").strip())
            if song_choice < 1 or song_choice > len(songs):
                print("❌ Invalid selection")
                return
            song_id = songs[song_choice - 1].id
        except ValueError:
            print("❌ Invalid input")
            return
        
        print("\nSelect playlist:")
        for i, playlist in enumerate(playlists, 1):
            print(f"  {i}. {playlist.name}")
        
        try:
            playlist_choice = int(input("Select playlist number: ").strip())
            if playlist_choice < 1 or playlist_choice > len(playlists):
                print("❌ Invalid selection")
                return
            playlist_id = playlists[playlist_choice - 1].id
        except ValueError:
            print("❌ Invalid input")
            return
        
        playlist_repo.add_song_to_playlist(playlist_id, song_id)
        print("✓ Song added to playlist successfully")
        
    except Exception as e:
        logger.error(f"Failed to add song to playlist: {e}")
        print(f"❌ Error: {e}")


def view_playlist_songs():
    """View songs in a playlist (demonstrates READ with relationship)."""
    try:
        print("\n--- View Playlist Songs ---")
        playlists = playlist_repo.read_all()
        
        if not playlists:
            print("No playlists in database")
            return
        
        print("\nSelect playlist:")
        for i, playlist in enumerate(playlists, 1):
            print(f"  {i}. {playlist.name}")
        
        try:
            choice = int(input("Select playlist number: ").strip())
            if choice < 1 or choice > len(playlists):
                print("❌ Invalid selection")
                return
            playlist = playlists[choice - 1]
        except ValueError:
            print("❌ Invalid input")
            return
        
        song_ids = playlist_repo.get_playlist_songs(playlist.id)
        
        if not song_ids:
            print(f"No songs in playlist: {playlist.name}")
            return
        
        print(f"\nSongs in '{playlist.name}' ({len(song_ids)} total):\n")
        for i, song_id in enumerate(song_ids, 1):
            song = song_repo.read_by_id(song_id)
            if song:
                print(f"{i}. {song.title}")
                print(f"   Artist: {song.artist} | Genre: {song.genre} | Duration: {song.duration}s")
        
    except Exception as e:
        logger.error(f"Failed to view playlist songs: {e}")
        print(f"❌ Error: {e}")


def main():
    """Main application loop.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        initialize_app()
        
        while True:
            display_menu()
            choice = input("Select operation: ").strip()
            
            if choice == "1":
                create_song()
            elif choice == "2":
                view_all_songs()
            elif choice == "3":
                search_songs_by_artist()
            elif choice == "4":
                search_songs_by_genre()
            elif choice == "5":
                create_user()
            elif choice == "6":
                view_all_users()
            elif choice == "7":
                find_user_by_username()
            elif choice == "8":
                create_playlist()
            elif choice == "9":
                view_all_playlists()
            elif choice == "10":
                view_user_playlists()
            elif choice == "11":
                add_song_to_playlist()
            elif choice == "12":
                view_playlist_songs()
            elif choice == "0":
                print("\nGoodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
        
        return 0
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"❌ Fatal error: {e}")
        return 1
    
    finally:
        shutdown_app()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
