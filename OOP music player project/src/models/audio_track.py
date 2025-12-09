from abc import ABC, abstractmethod
import uuid

class AudioTrack(ABC):
    def __init__(self, title, duration):
        self.__id = str(uuid.uuid4()) # unique identifier for the track
        self.__title = title
        self.__duration = duration # duration in seconds

    @property
    def id(self):
        return self.__id
    
    @property
    def title(self):
        return self.__title
    
    @property
    def duration(self):
        return self.__duration
    
    @abstractmethod
    def get_details(self):
        pass

    def __str__(self):
        return f"AudioTrack(id={self.id}, title={self.title}, duration={self.duration}s)"