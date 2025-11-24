from models.song import Song

class TrackFactory:
    @staticmethod
    def create_song(title, duration, artist, genre):
        if duration < 0:
            raise ValueError("Duration cannot be negative")
        return Song(title, duration, artist, genre)