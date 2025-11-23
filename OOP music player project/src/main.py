"""
Sprint 1 Prototype - Music Playlist Manager
Demonstrates Create + Read operations with the complete data layer.
"""

import logging
import sys
from src.database.connection import DatabaseConnection
from src.database.schema import DatabaseSchema
from src.repositories.song_repository import SongRepository
from src.repositories.user_repository import UserRepository
from src.repositories.playlist_repository import PlaylistRepository
from src.models.user import User
from src.models.playlist import Playlist
from src.services.track_factory import TrackFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_database():
    """Initialize database connection and schema."""
    logger.info("=" * 60)
    logger.info("INITIALIZING DATABASE")
    logger.info("=" * 60)
    
    db = DatabaseConnection("playlist_manager.db")
    db.connect()
    DatabaseSchema.initialize_database()
    
    logger.info("Database ready!")
    return db


def create_sample_songs(song_repo):
    """Create sample songs in database."""
    logger.info("\n" + "=" * 60)
    logger.info("CREATING SAMPLE SONGS")
    logger.info("=" * 60)
    
    songs_data = [
        ("Bohemian Rhapsody", 354, "Queen", "Rock"),
        ("Imagine", 183, "John Lennon", "Rock"),
        ("Stairway to Heaven", 482, "Led Zeppelin", "Rock"),
        ("Hotel California", 391, "Eagles", "Rock"),
        ("Let It Be", 243, "The Beatles", "Rock"),
        ("Smells Like Teen Spirit", 301, "Nirvana", "Grunge"),
        ("One", 447, "Metallica", "Metal"),
        ("Black", 368, "Pearl Jam", "Grunge"),
    ]
    
    created_songs = []
    for title, duration, artist, genre in songs_data:
        try:
            song = TrackFactory.create_song(title, duration, artist, genre)
            song_id = song_repo.create(song)
            logger.info(f"✓ Created: {title} by {artist} ({duration}s)")
            created_songs.append(song_id)
        except Exception as e:
            logger.error(f"✗ Failed to create song: {e}")
    
    logger.info(f"\nTotal songs created: {len(created_songs)}")
    return created_songs


def create_sample_users(user_repo):
    """Create sample users in database."""
    logger.info("\n" + "=" * 60)
    logger.info("CREATING SAMPLE USERS")
    logger.info("=" * 60)
    
    users_data = [
        ("alice", "alice@example.com"),
        ("bob", "bob@example.com"),
        ("charlie", "charlie@example.com"),
    ]
    
    created_users = []
    for username, email in users_data:
        try:
            user = User(username, email)
            user_id = user_repo.create(user)
            logger.info(f"✓ Created: {username} ({email})")
            created_users.append((user_id, username))
        except Exception as e:
            logger.error(f"✗ Failed to create user: {e}")
    
    logger.info(f"\nTotal users created: {len(created_users)}")
    return created_users


def create_sample_playlists(playlist_repo, user_ids, song_ids):
    """Create sample playlists and add tracks."""
    logger.info("\n" + "=" * 60)
    logger.info("CREATING SAMPLE PLAYLISTS")
    logger.info("=" * 60)
    
    if not user_ids or not song_ids:
        logger.error("Cannot create playlists without users and songs!")
        return []
    
    # Create playlists for first user
    owner_id = user_ids[0][0]
    playlist_data = [
        ("Rock Classics", [0, 1, 2, 3, 4]),
        ("Heavy Hitters", [1, 6, 7]),
    ]
    
    created_playlists = []
    for playlist_name, song_indices in playlist_data:
        try:
            playlist = Playlist(playlist_name, owner_id)
            playlist_id = playlist_repo.create(playlist)
            logger.info(f"\n✓ Created playlist: {playlist_name}")
            
            # Add tracks to playlist
            for idx, song_idx in enumerate(song_indices):
                if song_idx < len(song_ids):
                    playlist_repo.add_track(playlist_id, song_ids[song_idx])
                    logger.info(f"  → Added track {idx + 1}")
            
            created_playlists.append(playlist_id)
        except Exception as e:
            logger.error(f"✗ Failed to create playlist: {e}")
    
    logger.info(f"\nTotal playlists created: {len(created_playlists)}")
    return created_playlists


def read_operations_demo(song_repo, user_repo, playlist_repo, playlist_ids, user_ids):
    """Demonstrate READ operations."""
    logger.info("\n" + "=" * 60)
    logger.info("READ OPERATIONS DEMO")
    logger.info("=" * 60)
    
    # Read all songs
    logger.info("\n1. Reading all songs:")
    all_songs = song_repo.read_all()
    logger.info(f"Total songs in database: {len(all_songs)}")
    for song in all_songs[:3]:  # Show first 3
        logger.info(f"   • {song['title']} by {song['artist']} ({song['duration']}s)")
    if len(all_songs) > 3:
        logger.info(f"   ... and {len(all_songs) - 3} more")
    
    # Read songs by artist
    logger.info("\n2. Reading songs by Queen:")
    queen_songs = song_repo.read_by_artist("Queen")
    logger.info(f"Found {len(queen_songs)} song(s) by Queen")
    for song in queen_songs:
        logger.info(f"   • {song['title']} ({song['duration']}s, {song['genre']})")
    
    # Read songs by genre
    logger.info("\n3. Reading Rock genre songs:")
    rock_songs = song_repo.read_by_genre("Rock")
    logger.info(f"Found {len(rock_songs)} Rock song(s)")
    for song in rock_songs[:3]:
        logger.info(f"   • {song['title']} by {song['artist']}")
    
    # Read all users
    logger.info("\n4. Reading all users:")
    all_users = user_repo.read_all()
    logger.info(f"Total users in database: {len(all_users)}")
    for user in all_users:
        logger.info(f"   • {user['username']} ({user['email']})")
    
    # Read user by username
    if user_ids:
        logger.info("\n5. Reading user by username:")
        user_result = user_repo.read_by_username(user_ids[0][1])
        if user_result:
            logger.info(f"   • Found: {user_result['username']} - {user_result['email']}")
    
    # Read all playlists
    logger.info("\n6. Reading all playlists:")
    all_playlists = playlist_repo.read_all()
    logger.info(f"Total playlists in database: {len(all_playlists)}")
    for playlist in all_playlists:
        logger.info(f"   • {playlist['name']} (Owner: {playlist['owner_id'][:8]}...)")
    
    # Read playlist with tracks
    if playlist_ids:
        logger.info("\n7. Reading playlist contents:")
        playlist_id = playlist_ids[0]
        playlist_info = playlist_repo.read(playlist_id)
        if playlist_info:
            logger.info(f"Playlist: {playlist_info['name']}")
            tracks = playlist_repo.get_tracks(playlist_id)
            logger.info(f"Contains {len(tracks)} track(s):")
            for track in tracks:
                logger.info(f"   • {track['title']} by {track['artist']} ({track['duration']}s)")
            
            total_duration = playlist_repo.get_total_duration(playlist_id)
            logger.info(f"Total playlist duration: {total_duration} seconds ({total_duration // 60}m {total_duration % 60}s)")


def main():
    """Main entry point for Sprint 1 prototype."""
    try:
        logger.info("\n")
        logger.info("╔════════════════════════════════════════════════════════╗")
        logger.info("║   MUSIC PLAYLIST MANAGER - SPRINT 1 PROTOTYPE          ║")
        logger.info("║   Student B Implementation: Database Layer             ║")
        logger.info("╚════════════════════════════════════════════════════════╝")
        
        # Setup database
        db = setup_database()
        
        # Initialize repositories
        song_repo = SongRepository(db)
        user_repo = UserRepository(db)
        playlist_repo = PlaylistRepository(db)
        
        # CREATE operations
        song_ids = create_sample_songs(song_repo)
        user_ids = create_sample_users(user_repo)
        playlist_ids = create_sample_playlists(playlist_repo, user_ids, song_ids)
        
        # READ operations
        read_operations_demo(song_repo, user_repo, playlist_repo, playlist_ids, user_ids)
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("SPRINT 1 SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✓ Songs created: {len(song_ids)}")
        logger.info(f"✓ Users created: {len(user_ids)}")
        logger.info(f"✓ Playlists created: {len(playlist_ids)}")
        logger.info(f"✓ Database operations: CREATE, READ (all working)")
        logger.info(f"✓ Error handling: Transaction management implemented")
        logger.info(f"✓ Logging: All operations logged")
        logger.info("\n" + "=" * 60)
        logger.info("PROTOTYPE EXECUTION COMPLETED SUCCESSFULLY")
        logger.info("=" * 60 + "\n")
        
        # Cleanup
        db.disconnect()
        
    except Exception as e:
        logger.error(f"\n✗ FATAL ERROR: {e}")
        logger.error("Traceback:", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
