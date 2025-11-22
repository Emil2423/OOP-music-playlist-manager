from abc import ABC, abstractmethod
import uuid

class AudioTrack(ABC):
    def __init__(self, title: str, duration: int):
        self.__id = str(uuid.uuid4()) # unique identifier for the track
        self.__title = title
        self.__duration = duration # duration in seconds

    @property
    def id(self) -> str:
        return self.__id
    
    @property
    def title(self) -> str:
        return self.__title
    
    @property
    def duration(self) -> int:
        return self.__duration
    
    @abstractmethod
    def get_details(self) -> str:
        pass

    def __str__(self) -> str:
        return f"AudioTrack(id={self.id}, title={self.title}, duration={self.duration}s)"