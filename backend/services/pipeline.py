from api.routers.metrics import depth_duration_seconds
from api.routers.metrics import detection_duration_seconds
from api.routers.metrics import decode_duration_seconds
from utils.profiling import profile_step
from domain.detection_box_center import calculate_detection_box_center
import asyncio
from contracts.camera_metadata import DetectionMetadata
from contracts.camera_metadata import CameraMetadata
import cv2 as cv
import numpy as np


class ProcessingPipeline:
    def __init__(self, detector, depth_model, safety_detector, redis):
        self.detector = detector
        self.depth_model = depth_model
        self.safety_detector = safety_detector
        self.redis = redis

    def _decode_frame(self, fb):
        return cv.imdecode(np.frombuffer(fb, np.uint8), cv.IMREAD_COLOR)

    def _camera_metadata(
        self, camera_id, safety_detection, depth_points, boxes_center_ratio
    ) -> CameraMetadata:
        detection_metadata = [
            DetectionMetadata(depth=depth, xRatio=xRatio)
            for depth, xRatio in zip(depth_points, boxes_center_ratio)
        ]
        metadata = CameraMetadata(
            camera_id=camera_id,
            is_danger=True if safety_detection else False,
            detection_metadata=detection_metadata,
        )
        return metadata

    async def run(self, camera_id: str, frame_bytes, frame_count):
        loop = asyncio.get_running_loop()

        with profile_step(
            "frame_processing_time", decode_duration_seconds, camera_id, frame_count
        ):
            frame_bytes = await loop.run_in_executor(
                None, self._decode_frame, frame_bytes
            )

        with profile_step(
            "detection_duration_seconds",
            detection_duration_seconds,
            camera_id,
            frame_count,
        ):
            detection_task = loop.run_in_executor(
                None, self.detector.detect, frame_bytes
            )
            safety_task = loop.run_in_executor(
                None, self.safety_detector.detect, frame_bytes
            )
            detections, safety_detection = await asyncio.gather(
                detection_task, safety_task
            )

        boxes_center, boxes_center_ratio = calculate_detection_box_center(
            detections.detections, frame_bytes.shape[1]
        )

        depth_points = []
        if boxes_center:
            with profile_step(
                "depth_duration_seconds", depth_duration_seconds, camera_id, frame_count
            ):
                depth_points = await loop.run_in_executor(
                    None, self.depth_model.calculate_depth, frame_bytes, boxes_center
                )

        metadata = self._camera_metadata(
            camera_id, safety_detection, depth_points, boxes_center_ratio
        )

        await self.redis.publish("dashboard_stream", metadata.model_dump_json())
        # Even if the camera was disconnected, redis is still going to show its data, which is not accurate.
        # Instead, we set expiry date for the camera data.
        await self.redis.setex(
            f"camera:{camera_id}:latest",  # And this is the key, or tag
            10,  # in seconds
            metadata.model_dump_json(),
        )

        # Note that JSONResponse doesn't work here, as it is for HTTP
        return {"status": 200, "camera_id": camera_id}
