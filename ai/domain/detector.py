from abc import ABC, abstractmethod


class Detector(ABC):
    @abstractmethod
    def detect(self):
        pass

    @abstractmethod
    def train(self):
        pass

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def export(self):
        pass
