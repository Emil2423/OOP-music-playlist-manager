from models.audio_track import AudioTrack

class Song(AudioTrack):
    def __init__(self, title, duration, artist, genre):
        super().__init__(title, duration)
        self.__artist = artist
        self.__genre = genre

    @property
    def artist(self):
        return self.__artist
    
    @property
    def genre(self):
        return self.__genre
    
    def get_details(self):
        return f"Song: {self.title} by {self.artist} [{self.genre}] ({self.duration}s)"
    
    def __str__(self):
        return f"Song(id={self.id}, title={self.title}, artist={self.artist}, genre={self.genre}, duration={self.duration}s)"