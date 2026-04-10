# contracts/detector.py
from pydantic import BaseModel, Field
from typing import List


class BBox(BaseModel):
    class_id: int
    class_name: str
    conf: float = Field(ge=0, le=1)  # Great Equal - Low Equal
    data: tuple  # xmin, ymin, xmax, ymax, conf, class  -  Mostly being used in tracking
    xyxy: tuple[float, float, float, float]  # xmin, ymin, xmax, ymax

    # Give it a try also and check Pydantic Validators - @field_validator("param_name")
    @classmethod
    def from_yolo(
        cls, idx: int, boxes, names: dict[int, str]
    ) -> "BBox":  # <-  Yes, i know, it is str.
        id_val = int(boxes.cls[idx].item())
        return cls(  # represents the class itself.
            class_id=id_val,
            class_name=names[id_val],
            conf=boxes.conf[idx].item(),
            data=boxes.data[idx].flatten().tolist(),
            xyxy=boxes.xyxy[idx].flatten().tolist(),
        )


class DetectionResults(BaseModel):
    """
    You can easily return this to json, using .json to be able to send to API server.
    """

    detections: List[BBox]
    orig_shape: tuple[int, int]
