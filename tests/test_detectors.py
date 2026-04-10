from ai.detectors.yolo_detector import YOLO_Detector
from app.config import AppConfig
from ultralytics.utils.plotting import Annotator
import cv2 as cv
from ai.utils.hugging_face import hf_fetch_model

test_image = r"G:\MyComputer\Workspace\Projects\gp-tracking-dashboard\tracking_dashboard\ai\dummy_data\home fire smoke.jpg"

config = AppConfig()
annotator = Annotator(cv.imread(test_image))

safety_detection_path = hf_fetch_model(
    repo_id="e1250/safety_detection", filename="yolo_smoke_fire.pt"
)

# Person Detector
# yolo_detector = YOLO_Detector(model_path=config.yolo.model_path)
# Fire-Smoke Detector
print(safety_detection_path)
yolo_detector = YOLO_Detector(model_path=safety_detection_path)

detections = yolo_detector.detect(test_image).detections

for det in detections:
    print()
    annotator.box_label(det.xyxy, label=f"{det.class_name}")

output_image = annotator.result()
cv.imshow("Annotation", output_image)
cv.waitKey(0)
cv.destroyAllWindows()
