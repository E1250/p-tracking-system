from contextlib import contextmanager
import time
import mlflow


@contextmanager
def profile_step(
    expr_name: str,
    prometheus_logger,
    camera_id,
    frame_count=None,
    experiment: bool = False,
):
    """With statement utility to time block of code"""
    start_time = time.time()

    try:
        # Code inside with statement
        yield
    finally:
        duration = round(time.time() - start_time, 4)
        prometheus_logger.labels(camera_id).observe(duration)
        if experiment:
            mlflow.log_metric(
                expr_name,
                duration,
                frame_count,
            )
