import uuid
from models.audio_track import AudioTrack

class Playlist:
    def __init__(self, name, owner_id):
        self.__id = str(uuid.uuid4())  # unique identifier for the playlist
        self.__name = name
        self.__owner_id = owner_id
        self.__tracks = []  # List to hold AudioTrack objects

    @property
    def id(self):
        return self.__id
    
    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, value):
        self.__name = value
    
    @property
    def owner_id(self):
        return self.__owner_id
    
    @property
    def tracks(self):
        return self.__tracks

    def add_track(self, track):
        if not isinstance(track, AudioTrack):
            raise TypeError("Only AudioTrack instances can be added to the playlist.")
        self.__tracks.append(track)

    def remove_track(self, track_id):
        self.__tracks = [track for track in self.__tracks if track.id != track_id]

    def get_tracks(self):
        return self.__tracks
    
    @property
    def total_duration(self):
        return sum(track.duration for track in self.__tracks)
    
    def __str__(self):
        return f"Playlist(id={self.id}, name={self.name}, owner_id={self.owner_id}, total_tracks={len(self.__tracks)}, total_duration={self.total_duration}s)"