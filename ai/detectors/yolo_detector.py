"""YOLO Detector pull and use the last version of Ultralytics and then use it for detection"""
from ai.contracts.detector import BBox, DetectionResults
from ultralytics import YOLO
from pathlib import Path
from typing import List
from ai.domain.detector import Detector
from ai.utils.constants import YOLOExportFormats

class YOLO_Detector(Detector):
    def __init__(self, model_path:Path|str="", f16=False):
        self.model = YOLO(model_path)
        # self.model = self.model.eval()
        self.names = self.model.names
        self.f16 = f16

    def detect(self, frame) -> DetectionResults:
        """Detecting using YOLO model
        input: 
            frame
        return: 
            DetectionResults
        """
        results = self.model(frame, half=self.f16)[0]  # Use fload 16, it is faster on GPUs with the same accuracy. 
        boxes = results.boxes
        
        detections: List[BBox] = [BBox.from_yolo(i, boxes, self.names) for i in range(len(boxes.cls))]

        return DetectionResults(detections=detections)

    def train(self, data_path:Path, epochs:int, device:str=None, **kwargs):
        """Training and fine-tuning YOLO model
        
        return:
            training_results
        """
        
        return self.model.train(
            data = data_path,       # Path to training data folder.
            epochs = epochs,        # Number of training epochs.
            device = device,
            batch_size = kwargs["batch_size"],
            augment = kwargs["augment"],
            wandb = True,           # Profile using wandb. 
        )

    def validate(self):
        """Built-In validation for the YOLO model
        
        return: 
            metrics
        """
        return self.model.val()
        
    def export(self, output_format:YOLOExportFormats=YOLOExportFormats.onnx) -> str:
        # TODO, Tons of issue to export the model, it is not exporting at all. GPT says it is due to the new python version. 
        """Exporting YOLO model for productions
        
        return: 
            export path:str
        """
        return self.model.export(
            format=output_format.value,
        )