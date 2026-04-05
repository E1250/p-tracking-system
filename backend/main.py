from fastapi import FastAPI
# from prometheus_client import metrics
from ai.depth.depth_anything import DepthAnything
from ai.detectors.yolo_detector import YOLO_Detector
from config.settings import AppConfig
from api.routers.metrics import metrics_asgi_app
from infra.system_metrics import log_system_metrics
from api.routers import camera_stream
from api.routers import dashboard_stream
from api.routers import health
from contextlib import asynccontextmanager
from infra.logger_structlog import StructLogger
import asyncio
import mlflow
import torch
from huggingface_hub import hf_hub_download
import redis.asyncio as aioredis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This is on_event("startup") new alternative, Make sure you load models here.
    """
    
    settings = AppConfig()
    logger = StructLogger(settings=settings)
   
    logger.info("Starting Server.... ")
    asyncio.create_task(log_system_metrics(logger, logger_interval_sec=settings.intervals.system_metrics_seconds))    
    
    # Using this way to can store data. it is acts as a dict which holds instances
    app.state.detection_model = YOLO_Detector()

    safety_detection_path = hf_hub_download(repo_id="depth-anything/Depth-Anything-V2-Small", filename="depth_anything_v2_vits.pth")
    app.state.depth_model = DepthAnything(encoder=settings.depth.encoder, depth_model_path=settings.depth.model_path, DEVICE="cuda")

    safety_detection_path = hf_hub_download(repo_id="e1250/safety_detection", filename="yolo_smoke_fire.pt")
    app.state.safety_detection_model = YOLO_Detector(safety_detection_path)

    app.state.logger = logger
    app.state.settings = settings
    # app.state.camera_metadata = {}
    # app.state.dashboard_clients = set()
    # Redis(host="localhost", port=6379, db=0, decode_responses=True)
    app.state.redis = aioredis.from_url("redis://localhost:6379", db=0, decode_responses=True)
    # Cnecking connection to redis. 
    # Thinking of moving this to the health check. 
    try:
        await app.state.redis.ping()
        logger.info("Redis connected successfully...")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise e

    # Each camera should have its tracker to be able to work fine. 
    # app.state.camera_trackers = {}
    yield

    logger.warn("Shutting down the server....")
    torch.cuda.empty_cache()
    await app.state.redis.close()
    # You can remove connections and release gpu here .  

mlflow.set_tracking_uri("sqlite:///config/logs/mlflow.db")
mlflow.set_experiment("realtime-detection-system")
mlflow.enable_system_metrics_logging()

app = FastAPI(
    title="Tracking System Backend",
    description="real-time frame processing API",
    version="0.1.0",
    lifespan=lifespan
    )

# Routes
app.mount("/metrics", metrics_asgi_app)    # Starting Prometheus server attached to my server.
app.include_router(camera_stream.router, prefix="/detectors")
app.include_router(dashboard_stream.router, prefix="/dashboard")
app.include_router(health.router, prefix="/health")

@app.get("/")
async def root():
    return {"status": "Real-Time tracker backend is running..."}