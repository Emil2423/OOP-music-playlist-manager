from models.audio_track import AudioTrack

class Playlist:
    def __init__(self, name, owner_id):
        self.name = name
        self.owner_id = owner_id
        self.tracks = []  # List to hold AudioTrack objects

    def add_track(self, track):
        if not isinstance(track, AudioTrack):
            raise TypeError("Only AudioTrack instances can be added to the playlist.")
        self.tracks.append(track)

    def remove_track(self, track_id):
        self.tracks = [track for track in self.tracks if track.id != track_id]

    def get_tracks(self):
        return self.tracks
    
    @property
    def total_duration(self):
        return sum(track.duration for track in self.tracks)
    
    def __str__(self):
        return f"Playlist(name={self.name}, owner_id={self.owner_id}, total_tracks={len(self.tracks)}, total_duration={self.total_duration}s)"