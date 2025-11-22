from src.models.song import Song

class TrackFactory:
    @staticmethod
    def create_song(title: str, duration: int, artist: str, genre: str) -> Song:
        if duration < 0:
            raise ValueError("Duration cannot be negative")
        return Song(title, duration, artist, genre)