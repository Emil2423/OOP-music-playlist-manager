import uuid


class User:
    def __init__(self, username, email):
        self.__username = username
        self.__email = email
        self.__playlists = []  # List to hold Playlist objects
        self.__id = str(uuid.uuid4())  # unique identifier for the user

    def create_playlist(self, playlist_obj):
        if playlist_obj.owner_id != self.__id:
            raise ValueError("owner_id does not match")
        self.__playlists.append(playlist_obj)

    @property
    def id(self):
        return self.__id

    @property
    def playlists(self):
        return self.__playlists