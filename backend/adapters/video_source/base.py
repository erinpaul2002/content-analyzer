from abc import ABC, abstractmethod

class VideoSourceAdapter(ABC):
    @abstractmethod
    def get_video_id(self,url:str)-> str|None:
        raise NotImplementedError("Subclasses must implement this method")
    
    @abstractmethod
    def get_video_details(self,video_id:str)-> dict|None:
        raise NotImplementedError("Subclasses must implement this method")
    
    @abstractmethod
    def get_video_transcript(self,video_id:str)-> dict|None:
        raise NotImplementedError("Subclasses must implement this method")