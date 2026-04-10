def calculate_detection_box_center(detections, image_width: float):
    boxes_center = []
    boxes_center_ratio = []
    for box in detections:
        xmin, ymin, xmax, ymax = box.xyxy
        xcenter = (xmax + xmin) / 2
        ycenter = (ymax + ymin) / 2
        boxes_center.append((int(xcenter), int(ycenter)))
        boxes_center_ratio.append(xcenter / image_width)

    return (boxes_center, boxes_center_ratio)
