from typing import List
from pydantic import BaseModel


class DetectionMetadata(BaseModel):
    depth: float
    xRatio: float


class CameraMetadata(BaseModel):
    camera_id: str
    is_danger: bool = False
    detection_metadata: List[DetectionMetadata]
