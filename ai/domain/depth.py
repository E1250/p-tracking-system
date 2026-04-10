from abc import ABC, abstractmethod


class Depth(ABC):
    @abstractmethod
    def depth(self, frame):
        pass
