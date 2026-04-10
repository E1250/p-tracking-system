from abc import ABC, abstractmethod


class Tracker(ABC):
    @abstractmethod
    def track(self):
        """
        Tracking function
        """
        pass

    @abstractmethod
    def reset(self):
        """
        Used to resert the tracker (ex. IDs) when the camera close or pause for a while.
        """
        pass
