from api.dependencies import get_safety_detection_model
from api.dependencies import get_detection_model, get_depth_model
import asyncio
import itertools
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from pandas.core.frame import nested_data_to_arrays
from ai.contracts.detector import DetectionResults
from api.routers.metrics import active_cameras, decode_duration_seconds, depth_duration_seconds, detection_duration_seconds, frame_processing_duration_seconds
from contracts.camera_metadata import CameraMetadata, DetectionMetadata
import traceback
import mlflow
from utils.experiment import log_config

import cv2 as cv
import numpy as np
import time

router = APIRouter()

@router.websocket("/stream/{camera_id}")
async def websocket_detect(
    websocket: WebSocket, 
    camera_id:str,
    detector=Depends(get_detection_model),
    safety_detector=Depends(get_safety_detection_model),
    depth_model=Depends(get_depth_model)
    ):
    """
    WebSocket stream takes the frame pass it to the ai models, save it under the camera id provided in the url. 
    
     url here is:  ws://127.0.0.1:8000/detectors/stream/camera_id
    """
    # Yes, I asked the same questions, is using webscoket.app.state many times here is consuming.   after checking, it is not performance consuming. 
    state = websocket.app.state
    logger = state.logger
    # Using Depends is important and called Inversion Of Control (IoC)/ Dependency injection, and is important for testing.
    redis = state.redis

    # Accepting the connection from the client
    await websocket.accept()

    # Logging and tracking action    
    active_cameras.inc()
    logger.info(f"Client ID >>{camera_id}<< Connected...")
    
    if mlflow.active_run():
         mlflow.end_run()
    run = mlflow.start_run(run_name=f'camera_{camera_id}', nested=True)
    step_counter = itertools.count()
    log_config()

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
        except WebScoketDisconnect:
            raise
    
    async def process_frames():


        try:
            # What are the info you aim to collect from the camera? 
            # How many frames received by second. 
            # Frame processing time. 
            # Average processing time  for logger. 
            # Model processing time. 

            # frame_count = itertools.count()

            logger.info(f"Camera {camera_id} start sending frames...")

            def decode_frame():
                # Decode image
                return cv.imdecode(np.frombuffer(frame_bytes, np.uint8), cv.IMREAD_COLOR)        

            # Keep receiving messages in a loop until disconnection. 
            while True:

                frame_bytes = await frame_queue.get()
                
                # Profiling
                t0 = time.time()            

                image_array = await loop.run_in_executor(None, decode_frame)
                decode_duration_seconds.labels(camera_id).observe(round(time.time() - t0, 3))
                mlflow.log_metric("frame_processing_time", round(time.time() - t0, 3), next(step_counter))

                detection_task = loop.run_in_executor(None, detector.detect, image_array)
                safety_task = loop.run_in_executor(None, safety_detector.detect, image_array)

                detections, safety_detection = await asyncio.gather(detection_task, safety_task)
                detection_duration_seconds.labels(camera_id).observe(round(time.time() - t0, 3))
                mlflow.log_metric("detection_duration_seconds", round(time.time() - t0, 3), next(step_counter))

                # Profiling
                frame_processing_duration_seconds.labels(camera_id).observe(round(time.time() - t0, 3))
                logger.debug("Frame processed", camera_id=camera_id)
                mlflow.log_metric("frame_processing duration time", round(time.time() - t0, 3), next(step_counter))

                boxes_center = []
                boxes_center_ratio = []
                for box in detections.detections:
                    print(type(box))
                    xmin, ymin, xmax, ymax = box.xyxy
                    xcenter = (xmax + xmin) / 2
                    ycenter = (ymax + ymin) / 2
                    boxes_center.append((int(xcenter), int(ycenter)))
                    boxes_center_ratio.append(xcenter / image_array.shape[1])
                
                depth_points = await loop.run_in_executor(None, depth_model.calculate_depth, image_array, boxes_center) if boxes_center else []
                depth_duration_seconds.labels(camera_id).observe(round(time.time() - t0, 3))
                mlflow.log_metric("depth_duration_seconds", round(time.time() - t0, 3), next(step_counter))

                detection_metadata = [DetectionMetadata(depth=depth, xRatio=xRatio) for depth, xRatio in zip(depth_points, boxes_center_ratio)]
                metadata = CameraMetadata(camera_id=camera_id, is_danger = True if safety_detection else False, detection_metadata=detection_metadata)
                
                # state.camera_metadata[camera_id] = metadata.model_dump()
                await redis.publish("dashboard_stream", metadata.model_dump_json())
                # Even if the camera was disconnected, redis is still going to show its data, which is not accurate.
                # Instead, we set expiry date for the camera data.
                await redis.setex(
                    f"camera:{camera_id}:latest", # And this is the key, or tag
                    10, # in seconds
                    metadata.model_dump_json()
                )

                # Note that JSONResponse doesn't work here, as it is for HTTP
                await websocket.send_json({"status": 200, "camera_id": camera_id})
        
        except Exception as e:
            logger.error(f"Processing Error: {e}", camera_id=camera_id)
            raise

    try:
        await asyncio.gather(
            receive_frames(),
            process_frames()
        )

    except WebSocketDisconnect:
        logger.warn(f"Client ID >>{camera_id}<< Disconnected Normally...")
        # state.camera_metadata.pop(camera_id, None)

    except Exception as e:
        logger.error(f"Error in websocker, Client ID: >>{camera_id}<<: {e}")
        traceback.print_exc() # This one is actually really better, it shows more details about the issue happened. 
        # Also work on and create the logger.exception, as it directly controls printing more details about the issue happened.
        await websocket.close()

    finally:
        active_cameras.dec()
        mlflow.end_run()


# Uncomment this when needed, It is the same but using HTTP, which is Request Response only. could be used for testing. 
# from fastapi import Request, UploadFile
# @router.post("/detect")
# async def post_detection(request: Request, file: UploadFile):
#     # Request here is being used to access the app.state.model

#     request.app.state.model.detect(file)