from services.pipeline import ProcessingPipeline
from api.dependencies import get_safety_detection_model
from api.dependencies import get_detection_model, get_depth_model
import asyncio
import itertools
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from api.routers.metrics import (
    active_cameras,
)
import mlflow
from utils.experiment import log_config


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
    pipeline = ProcessingPipeline(detector, depth_model, safety_detector, redis)

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

            # Keep receiving messages in a loop until disconnection.
            while True:
                frame_bytes = await frame_queue.get()

                try:
                    results = await pipeline.run(
                        camera_id, frame_bytes, next(step_counter)
                    )
                except Exception as e:
                    logger.warn(
                        f"Error happened while processing a frame in {camera_id}: {e}"
                    )
                    logger.exception(e)
                    continue

                # Note that JSONResponse doesn't work here, as it is for HTTP
                await websocket.send_json(results)

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
