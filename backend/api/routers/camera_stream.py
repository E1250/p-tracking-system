from backend.domain.detection_box_center import calculate_detection_box_center
from api.dependencies import get_safety_detection_model
from api.dependencies import get_detection_model, get_depth_model
import asyncio
import itertools
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from api.routers.metrics import (
    active_cameras,
    decode_duration_seconds,
    depth_duration_seconds,
    detection_duration_seconds,
    frame_processing_duration_seconds,
)
from contracts.camera_metadata import CameraMetadata, DetectionMetadata
import mlflow
from utils.experiment import log_config

import cv2 as cv
import numpy as np
import time

router = APIRouter()


@router.websocket("/stream/{camera_id}")
async def websocket_detect(
    websocket: WebSocket,
    camera_id: str,
    detector=Depends(get_detection_model),
    safety_detector=Depends(get_safety_detection_model),
    depth_model=Depends(get_depth_model),
):
    """
    WebSocket stream takes the frame pass it to the ai models, save it under the camera id provided in the url.

     url here is:  ws://127.0.0.1:8000/detectors/stream/camera_id
    """
    # Yes, I asked the same questions, is using webscoket.app.state many times here is consuming. after checking, it is not performance consuming.
    state = websocket.app.state
    logger = state.logger
    # Using Depends is important and called Inversion Of Control (IoC)/ Dependency injection, and is important for testing.
    redis = state.redis

    # Accepting the connection from the client
    await websocket.accept()

    # Logging and tracking action
    active_cameras.inc()
    await redis.sadd(
        "cameras:active", camera_id
    )  # Save connected camera name into redis
    logger.info(f"Client ID >>{camera_id}<< Connected...")

    step_counter = itertools.count()

    loop = asyncio.get_running_loop()
    # Queue removing old images in case they were being stacked
    frame_queue: asyncio.Queue = asyncio.Queue(maxsize=1)

    async def receive_frames():
        """Receive and Queue frames, keep the latest one"""
        try:
            while True:
                frame_bytes = await websocket.receive_bytes()

                if frame_queue.full():
                    try:
                        frame_queue.get_nowait()
                        logger.debug("Frame Dropped", camera_id=camera_id)
                    except asyncio.QueueEmpty:
                        pass

                await frame_queue.put(frame_bytes)
        except WebSocketDisconnect:
            raise

    async def process_frames():
        try:
            logger.info(f"Camera {camera_id} start sending frames...")

            def decode_frame(fb):
                return cv.imdecode(np.frombuffer(fb, np.uint8), cv.IMREAD_COLOR)

            # Keep receiving messages in a loop until disconnection.
            while True:
                frame_bytes = await frame_queue.get()

                # Profiling
                t0 = time.time()
                image_array = await loop.run_in_executor(
                    None, decode_frame, frame_bytes
                )
                decode_duration_seconds.labels(camera_id).observe(
                    round(time.time() - t0, 3)
                )
                mlflow.log_metric(
                    "frame_processing_time",
                    round(time.time() - t0, 3),
                    next(step_counter),
                )

                # Apply detection models
                t0 = time.time()
                detection_task = loop.run_in_executor(
                    None, detector.detect, image_array
                )
                safety_task = loop.run_in_executor(
                    None, safety_detector.detect, image_array
                )
                detections, safety_detection = await asyncio.gather(
                    detection_task, safety_task
                )
                detection_duration_seconds.labels(camera_id).observe(
                    round(time.time() - t0, 3)
                )
                mlflow.log_metric(
                    "detection_duration_seconds",
                    round(time.time() - t0, 3),
                    next(step_counter),
                )

                # Profiling
                frame_processing_duration_seconds.labels(camera_id).observe(
                    round(time.time() - t0, 3)
                )
                logger.debug("Frame processed", camera_id=camera_id)
                mlflow.log_metric(
                    "frame_processing duration time",
                    round(time.time() - t0, 3),
                    next(step_counter),
                )

                boxes_center, boxes_center_ratio = calculate_detection_box_center(detections.detections, image_array.shape[1])

                t0 = time.time()
                depth_points = (
                    await loop.run_in_executor(
                        None, depth_model.calculate_depth, image_array, boxes_center
                    )
                    if boxes_center
                    else []
                )
                depth_duration_seconds.labels(camera_id).observe(
                    round(time.time() - t0, 3)
                )
                mlflow.log_metric(
                    "depth_duration_seconds",
                    round(time.time() - t0, 3),
                    next(step_counter),
                )

                detection_metadata = [
                    DetectionMetadata(depth=depth, xRatio=xRatio)
                    for depth, xRatio in zip(depth_points, boxes_center_ratio)
                ]
                metadata = CameraMetadata(
                    camera_id=camera_id,
                    is_danger=True if safety_detection else False,
                    detection_metadata=detection_metadata,
                )

                await redis.publish("dashboard_stream", metadata.model_dump_json())
                # Even if the camera was disconnected, redis is still going to show its data, which is not accurate.
                # Instead, we set expiry date for the camera data.
                await redis.setex(
                    f"camera:{camera_id}:latest",  # And this is the key, or tag
                    10,  # in seconds
                    metadata.model_dump_json(),
                )

                # Note that JSONResponse doesn't work here, as it is for HTTP
                await websocket.send_json({"status": 200, "camera_id": camera_id})

        except Exception as e:
            logger.error(f"Processing Error: {e}", camera_id=camera_id)
            raise

    with mlflow.start_run(
        run_name=f"camera_{camera_id}", nested=True, parent_run_id=state.mlflow_run_id
    ):
        log_config()

        try:
            await asyncio.gather(receive_frames(), process_frames())

        except WebSocketDisconnect:
            logger.warn(f"Client ID >>{camera_id}<< Disconnected Normally...")

        except Exception as e:
            logger.error(f"Error in websocker, Client ID: >>{camera_id}<<: {e}")
            logger.exception(e)
            # This one is actually really better, it shows more details about the issue happened.
            # Also work on and create the logger.exception, as it directly controls printing more details about the issue happened.
            await websocket.close()

        finally:
            await redis.srem(
                "cameras:active", camera_id
            )  # Remove the camera from redis connected cameras
            active_cameras.dec()
