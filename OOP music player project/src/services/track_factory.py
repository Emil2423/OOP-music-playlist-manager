import logging
from models.song import Song

logger = logging.getLogger(__name__)


class TrackFactory:
    """Factory class for creating track objects.
    
    Uses Factory Pattern to encapsulate object creation logic.
    """
    
    @staticmethod
    def create_song(title, duration, artist, genre):
        """Create a new Song instance.
        
        Args:
            title: Song title
            duration: Duration in seconds
            artist: Artist name
            genre: Music genre
            
        Returns:
            Song: New Song instance
            
        Raises:
            ValueError: If duration is negative
        """
        logger.info(f"TrackFactory creating song: title='{title}', artist='{artist}', genre='{genre}'")
        
        if duration < 0:
            logger.warning(f"Invalid duration {duration} for song '{title}' - duration cannot be negative")
            raise ValueError("Duration cannot be negative")
        
        song = Song(title, duration, artist, genre)
        logger.debug(f"Song created successfully via factory: id={song.id}, title='{title}'")
        return song