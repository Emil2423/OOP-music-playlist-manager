from src.models.audio_track import AudioTrack

class Song(AudioTrack):
    def __init__(self, title: str, duration: int, artist: str, genre: str):
        super().__init__(title, duration)
        self.__artist = artist
        self.__genre = genre

    @property
    def artist(self) -> str:
        return self.__artist
    
    @property
    def genre(self) -> str:
        return self.__genre
    
    def get_details(self) -> str:
        return f"Song: {self.title} by {self.artist} [{self.genre}] ({self.duration}s)"
    
    def __str__(self) -> str:
        return f"Song(id={self.id}, title={self.title}, artist={self.artist}, genre={self.genre}, duration={self.duration}s)"