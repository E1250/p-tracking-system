from ultralytics import YOLO
from ai.domain.tracker import Tracker


class YoloTracker(Tracker):
    def __init__(self, yolo_detection_model: YOLO, tracker_name: str):
        self.model = yolo_detection_model
        self.tracker_name = tracker_name

    def track(self, frame):
        pass

    def reset(self):
        # YOLO doesn't support reset for now...
        pass
