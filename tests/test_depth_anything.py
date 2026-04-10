import torch
from ai.depth.depth_anything import DepthAnything
from app.config import AppConfig
import cv2 as cv

config = AppConfig()

DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)
image_path = r"G:\MyComputer\Workspace\Projects\gp-tracking-dashboard\tracking_dashboard\ai\dummy_data\black tesla car.png"
depth_model_path = config.depth.model_path


depth_anything = DepthAnything(
    DEVICE=DEVICE, depth_model_path=depth_model_path, encoder="vits"
)

# depth = depth_anything.depth(image_path)
# cv.imshow("Depth", depth)
# cv.waitKey(0)
# cv.destroyAllWindows()

depth = depth_anything.calculate_depth(cv.imread(image_path), [(50, 50)])
print(depth)
