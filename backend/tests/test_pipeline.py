from services.pipeline import ProcessingPipeline
import pytest
import numpy as np
from unittest.mock import MagicMock, AsyncMock, patch


@pytest.fixture
def mock_deps():
    return {
        "detector": MagicMock(),
        "safety": MagicMock(),
        "depth": MagicMock(),
        "redis": AsyncMock(),
    }


@pytest.mark.asyncio
async def test_pipeline_success(mock_deps):
    mock_detection = MagicMock()
    mock_detection.xyxy = [10, 10, 20, 20]
    mock_detection.class_name = "person"

    # Settings mock models values
    mock_deps["detector"].detect.return_value.detections = [mock_detection]
    mock_deps["safety"].detect.return_value = []  # No dangers

    pipeline = ProcessingPipeline(
        detector=mock_deps["detector"],
        safety_detector=mock_deps["safety"],
        depth_model=mock_deps["depth"],
        redis=mock_deps["redis"],
    )

    with (
        patch("cv2.imdecode") as mock_decode,
        patch("utils.profiling.mlflow") as _,
    ):
        mock_decode.return_value = np.zeros((100, 100, 3), dtype=np.uint8)

        result = await pipeline.run(
            camera_id="test", frame_bytes=b"test", frame_count=1
        )

    assert result["status"] == 200

    mock_deps["depth"].calculate_depth.assert_called_once()
    mock_deps["redis"].publish.assert_called_once()


@pytest.mark.asyncio
async def test_pipeline_no_detections(mock_deps):
    mock_deps["detector"].detect.return_value.detections = []

    pipeline = ProcessingPipeline(
        detector=mock_deps["detector"],
        safety_detector=mock_deps["safety"],
        depth_model=mock_deps["depth"],
        redis=mock_deps["redis"],
    )

    with (
        patch("cv2.imdecode") as mock_decode,
        patch("utils.profiling.mlflow") as _,
    ):
        mock_decode.return_value = np.zeros((100, 100, 3), dtype=np.uint8)

        await pipeline.run(camera_id="test", frame_bytes=b"test", frame_count=1)

    mock_deps["depth"].calculate_depth.assert_not_called()
