from abc import ABC, abstractmethod

class TranscriptStorageAdapter(ABC):
    @abstractmethod
    def save(self, video_id: str, payload: dict) -> str:
        raise NotImplementedError

    @abstractmethod
    def load(self, video_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def exists(self, video_id: str) -> bool:
        raise NotImplementedError