"""
detector.py - Real Object Detection using Ultralytics YOLO

This module loads a lightweight YOLO model once upon module import and exposes
the `detect_objects(source)` function to run object detection on an image path
or OpenCV frame/ndarray.
"""

from ultralytics import YOLO

# 1. Load small pretrained YOLO model once at module import time (lightweight for beginner laptops)
MODEL_NAME = "yolov8n.pt"
model = YOLO(MODEL_NAME)
MIN_CONFIDENCE = 0.35


def detect_objects(source):
    """
    Runs YOLO object detection on the provided source.

    :param source: Image file path (str) or OpenCV image/frame (numpy ndarray).
    :return: A list of dictionaries, where each dictionary contains:
             - class_name (str): Name of detected class
             - confidence (float): Confidence score
             - x1, y1, x2, y2 (float): Bounding box coordinates
    """
    # Perform inference (verbose=False keeps console output clean)
    results = model(source, conf=MIN_CONFIDENCE, iou=0.45, imgsz=640, verbose=False)

    detections = []
    for r in results:
        boxes = r.boxes
        for box in boxes:
            cls_id = int(box.cls[0].item())
            class_name = model.names.get(cls_id, str(cls_id))
            confidence = round(float(box.conf[0].item()), 4)
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detections.append({
                "class_name": class_name,
                "confidence": confidence,
                "x1": round(float(x1), 2),
                "y1": round(float(y1), 2),
                "x2": round(float(x2), 2),
                "y2": round(float(y2), 2)
            })

    return detections


def detect_objects_stub(image_input=None) -> dict:
    """
    Legacy prototype stub function maintained for backwards compatibility with app.py.
    """
    mock_flags = {
        "person_detected": True,
        "vehicle_detected": True,
        "person_near_vehicle": True,
        "helmet_missing": True,
        "safety_vest_missing": False,
        "restricted_zone": False,
        "fall_detected": False
    }

    mock_detections = [
        {"class": "person", "confidence": 0.92, "box": [100, 150, 200, 400]},
        {"class": "vehicle", "confidence": 0.88, "box": [180, 160, 500, 600]}
    ]

    return {
        "flags": mock_flags,
        "detections": mock_detections
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python detector.py <path_to_image>")
    else:
        image_path = sys.argv[1]
        results = detect_objects(image_path)
        print(f"Found {len(results)} object(s):")
        for det in results:
            print(det)


