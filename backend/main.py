from ai.utils.hugging_face import hf_fetch_model
from ai.depth.depth_anything import DepthAnything
from ai.detectors.yolo_detector import YOLO_Detector
from config.settings import AppConfig
from api.routers.metrics import metrics_asgi_app
from api.routers import camera_stream
from api.routers import dashboard_stream
from api.routers import health
from infra.logger_structlog import StructLogger

from contextlib import asynccontextmanager
import mlflow
import torch
import redis.asyncio as aioredis
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import dagshub
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This is on_event("startup") new alternative, Make sure you load models here.
    """

    settings = AppConfig()
    logger = StructLogger(settings=settings)
    # Using this way to can store data. it is acts as a dict which holds instances
    app.state.logger = logger
    app.state.settings = settings
    app.state.mlflow_run_id = parent_run.info.run_id

    logger.info("Starting Server.... ")
    # asyncio.create_task(log_system_metrics(logger, logger_interval_sec=settings.intervals.system_metrics_seconds))

    detection_model_path = hf_fetch_model(
        repo_id="Ultralytics/YOLO26", filename=settings.yolo.model_name
    )
    app.state.detection_model = YOLO_Detector(detection_model_path)

    depth_model_path = hf_fetch_model(
        repo_id="depth-anything/Depth-Anything-V2-Small",
        filename=settings.depth.model_name,
    )
    app.state.depth_model = DepthAnything(
        encoder=settings.depth.encoder,
        depth_model_path=depth_model_path,
        DEVICE=settings.depth.device,
    )

    safety_detection_path = hf_fetch_model(
        repo_id="e1250/safety_detection", filename=settings.security_detector.model_name
    )
    app.state.safety_detection_model = YOLO_Detector(safety_detection_path)

    app.state.redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    # Checking connection to redis - TODO add to health check
    try:
        await app.state.redis.ping()
        logger.info("Redis connected successfully...")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise e

    yield

    # Here You remove connections and release gpu here..
    logger.warn("Shutting down the server....")
    torch.cuda.empty_cache()
    await app.state.redis.close()


# MLFlow setup
dagshub.init(repo_owner="eslam760000", repo_name="p-tracking_system", mlflow=True)
mlflow.set_tracking_uri("sqlite:///config/logs/mlflow.db")
mlflow.set_experiment("realtime-detection-system")
parent_run = mlflow.start_run(run_name="server_session")
mlflow.enable_system_metrics_logging()

app = FastAPI(
    title="Tracking System Backend",
    description="real-time frame processing API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Routes
app.mount(
    "/metrics", metrics_asgi_app
)  # Starting Prometheus server attached to my server.
app.include_router(camera_stream.router, prefix="/detectors")
app.include_router(dashboard_stream.router, prefix="/dashboard")
app.include_router(health.router, prefix="/health")


@app.get("/")
async def root():
    return {"status": "Real-Time tracker backend is running..."}
