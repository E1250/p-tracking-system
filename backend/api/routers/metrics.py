# Prometheus is for real-time system health.
# Grafana visualize the output of Prometheus
# This is considered as Monitoring
from prometheus_client import Histogram, Gauge, make_asgi_app

metrics_asgi_app = make_asgi_app()


active_cameras = Gauge(
    "active_camera_connections", "Number of Currently Connected camera websockets"
)

active_dashboards = Gauge(
    "active_dashboards", "Number of active dashboards which fetching data"
)

frame_processing_duration_seconds = Histogram(
    "frame_processing_duration_seconds", "Time to process one frame", ["camera_id"]
)

decode_duration_seconds = Histogram(
    "decode_duration_seconds", "Time to decode one image", ["camera_id"]
)
detection_duration_seconds = Histogram(
    "detection_duration_seconds", "Time to detect", ["camera_id"]
)
depth_duration_seconds = Histogram(
    "depth_duration_seconds", "Time to calculate the depth", ["camera_id"]
)


cpu_usage = Gauge("cpu_usage_percent", "CPU usage %")
mem_usage = Gauge("mem_usage_percent", "mem usage %")

active_workers = Gauge("active_workers", "Active threads")
