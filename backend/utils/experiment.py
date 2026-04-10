from backend.config.settings import AppConfig
import mlflow

config = AppConfig()


def log_config():
    mlflow.log_param("Detector", config.yolo.model_name)
    mlflow.log_param("Safety Model", config.security_detector.model_name)
    mlflow.log_param("Depth Model", config.depth.model_name)


def log_metrics(metrics: dict):
    for k, v in metrics.items():
        mlflow.log_metric(k, v)
