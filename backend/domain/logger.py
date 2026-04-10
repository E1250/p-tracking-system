from abc import ABC, abstractmethod

class Logger(ABC):
    @abstractmethod
    def info(self, msg: str, **kwargs):
        pass

    def debug(self, msg: str, **kwargs):
        pass

    @abstractmethod
    def error(self, msg: str, **kwargs):
        pass

    @abstractmethod
    def warn(self, msg: str, **kwargs):
        pass

    @abstractmethod
    def exception(self, msg: str, **kwargs):
        pass