"""YOLO Detector pull and use the last version of Ultralytics and then use it for detection"""

from ai.contracts.detector import BBox, DetectionResults
from ultralytics import YOLO
from pathlib import Path
from typing import List
from ai.domain.detector import Detector


class YOLO_Detector(Detector):
    def __init__(self, model_path: Path | str = "yolo26n.pt", f16=False):
        self.model = YOLO(model=model_path)
        self.names = self.model.names
        self.f16 = f16

    def detect(self, frame) -> DetectionResults:
        """Detecting using YOLO model
        input:
            frame
        return:
            DetectionResults
        """
        results = self.model(frame, half=self.f16)[
            0
        ]  # Use fload 16, it is faster on GPUs with the same accuracy.
        boxes = results.boxes

        detections: List[BBox] = [
            BBox.from_yolo(i, boxes=boxes, names=self.names)
            for i in range(len(boxes.cls))
        ]

        return DetectionResults(detections=detections, orig_shape=boxes.orig_shape)

    def train(self, data_path: Path, epochs: int, device: str, **kwargs):
        pass

    def validate(self):
        pass

    def export(self, output_format) -> str:
        pass
