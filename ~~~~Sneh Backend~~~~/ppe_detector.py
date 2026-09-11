"""
ppe_detector.py - Personal Protective Equipment (PPE) Detection Module

This module checks whether detected workers/people are wearing required PPE:
1. Safety Helmet
2. Safety Vest

MODEL LIMITATION NOTE:
The standard YOLOv8n model (yolov8n.pt) trained on the COCO dataset contains 80 classes
including 'person' and 'vehicle' types (car, bus, truck, etc.), but does NOT contain
PPE classes like 'helmet' or 'vest'. Therefore, PPE detection relies on secondary PPE
object detections (when custom PPE weights/detections are provided) or image Region of
Interest (ROI) color/feature inspection on person crops, with configurable confidence
thresholds and explicit uncertainty states.
"""

import math
import numpy as np

# Configurable default confidence thresholds
DEFAULT_CONFIDENCE_THRESHOLD = 0.50
DEFAULT_UNCERTAINTY_THRESHOLD = 0.30

# PPE class aliases for flexible matching
HELMET_POSITIVE_CLASSES = {"helmet", "safety_helmet", "hard_hat", "hardhat", "head_protection"}
HELMET_NEGATIVE_CLASSES = {"no_helmet", "no_hard_hat", "no_hardhat", "bare_head"}

VEST_POSITIVE_CLASSES = {"vest", "safety_vest", "hi_vis_vest", "reflective_vest", "high_vis_vest"}
VEST_NEGATIVE_CLASSES = {"no_vest", "no_safety_vest", "no_hi_vis_vest"}


def is_point_in_box(point: tuple, box: dict, margin_pct: float = 0.10) -> bool:
    """
    Checks if a point (x, y) lies inside a bounding box dictionary (with an optional margin).
    """
    px, py = point
    w = box["x2"] - box["x1"]
    h = box["y2"] - box["y1"]
    margin_x = w * margin_pct
    margin_y = h * margin_pct

    return (
        (box["x1"] - margin_x) <= px <= (box["x2"] + margin_x) and
        (box["y1"] - margin_y) <= py <= (box["y2"] + margin_y)
    )


def analyze_person_roi_hsv(image: np.ndarray, person_box: dict) -> dict:
    """
    Analyzes an image crop of a detected person for high-visibility vest color signatures
    (bright yellow, orange, neon green) and head region luminance/color consistency.

    :param image: OpenCV BGR image (numpy ndarray)
    :param person_box: Dictionary with 'x1', 'y1', 'x2', 'y2'
    :return: Dictionary with vest and helmet ROI scores & confidences
    """
    try:
        import cv2

        img_h, img_w = image.shape[:2]
        x1 = max(0, int(person_box["x1"]))
        y1 = max(0, int(person_box["y1"]))
        x2 = min(img_w, int(person_box["x2"]))
        y2 = min(img_h, int(person_box["y2"]))

        box_w = x2 - x1
        box_h = y2 - y1

        if box_w < 10 or box_h < 20:
            # ROI too small for reliable analysis -> mark UNCERTAIN
            return {
                "vest_score": 0.0,
                "vest_confidence": 0.35,
                "helmet_score": 0.0,
                "helmet_confidence": 0.35
            }

        person_crop = image[y1:y2, x1:x2]

        # 1. Torso Region (20% to 65% of person height)
        torso_y1 = int(box_h * 0.20)
        torso_y2 = int(box_h * 0.65)
        torso_crop = person_crop[torso_y1:torso_y2, :]

        if torso_crop.size > 0:
            hsv_torso = cv2.cvtColor(torso_crop, cv2.COLOR_BGR2HSV)

            # High-vis Yellow/Lime HSV range
            lower_yellow = np.array([20, 100, 100])
            upper_yellow = np.array([40, 255, 255])
            mask_yellow = cv2.inRange(hsv_torso, lower_yellow, upper_yellow)

            # High-vis Orange HSV range
            lower_orange = np.array([5, 120, 120])
            upper_orange = np.array([19, 255, 255])
            mask_orange = cv2.inRange(hsv_torso, lower_orange, upper_orange)

            combined_mask = cv2.bitwise_or(mask_yellow, mask_orange)
            vis_pixel_ratio = np.sum(combined_mask > 0) / float(torso_crop.shape[0] * torso_crop.shape[1])

            if vis_pixel_ratio >= 0.12:
                vest_score = 1.0
                vest_conf = min(0.95, round(0.70 + vis_pixel_ratio, 2))
            elif vis_pixel_ratio <= 0.03:
                vest_score = 0.0
                vest_conf = round(0.80 - vis_pixel_ratio, 2)
            else:
                vest_score = 0.5
                vest_conf = 0.40  # Uncertain range
        else:
            vest_score = 0.0
            vest_conf = 0.30

        # 2. Head Region (top 25% of height)
        head_y2 = int(box_h * 0.25)
        head_crop = person_crop[0:head_y2, :]

        if head_crop.size > 0:
            # Check for hardhat / helmet color prominence (bright yellow, white, red, blue, orange)
            hsv_head = cv2.cvtColor(head_crop, cv2.COLOR_BGR2HSV)
            # High brightness or strong safety helmet color
            val_channel = hsv_head[:, :, 2]
            high_brightness_ratio = np.sum(val_channel > 200) / float(head_crop.shape[0] * head_crop.shape[1])

            if high_brightness_ratio >= 0.20:
                helmet_score = 1.0
                helmet_conf = min(0.90, round(0.65 + high_brightness_ratio, 2))
            elif high_brightness_ratio <= 0.04:
                helmet_score = 0.0
                helmet_conf = round(0.75 - high_brightness_ratio, 2)
            else:
                helmet_score = 0.5
                helmet_conf = 0.40
        else:
            helmet_score = 0.0
            helmet_conf = 0.30

        return {
            "vest_score": vest_score,
            "vest_confidence": vest_conf,
            "helmet_score": helmet_score,
            "helmet_confidence": helmet_conf
        }

    except Exception:
        # Fallback if OpenCV or crop fails
        return {
            "vest_score": 0.0,
            "vest_confidence": 0.30,
            "helmet_score": 0.0,
            "helmet_confidence": 0.30
        }


def detect_ppe(
    source=None,
    detections: list = None,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    uncertainty_threshold: float = DEFAULT_UNCERTAINTY_THRESHOLD,
    custom_ppe_detections: list = None
) -> dict:
    """
    Evaluates PPE (helmet and safety vest) compliance for each detected person.

    :param source: OpenCV image frame (numpy ndarray), file path, or None.
    :param detections: List of object detection dicts (containing 'class_name', 'x1', 'y1', 'x2', 'y2', 'confidence').
    :param confidence_threshold: Minimum confidence to confirm DETECTED or NOT_DETECTED (default: 0.50).
    :param uncertainty_threshold: Threshold below which status is UNCERTAIN (default: 0.30).
    :param custom_ppe_detections: Optional list of explicit PPE bounding box detections (helmet, vest, etc.).
    :return: Dictionary containing structured person PPE results and summary statistics.
    """
    if detections is None:
        detections = []

    # 1. Filter all detected people
    people = []
    for det in detections:
        if det.get("class_name", "").lower() == "person":
            people.append(det)

    if not people:
        return {
            "people": [],
            "summary": {
                "people_count": 0,
                "helmet_detected_count": 0,
                "helmet_missing_count": 0,
                "vest_detected_count": 0,
                "vest_missing_count": 0,
                "uncertain_count": 0
            },
            "confidence_threshold": confidence_threshold,
            "uncertainty_threshold": uncertainty_threshold
        }

    ppe_boxes = custom_ppe_detections or []

    # Separate any PPE boxes passed within general detections if present
    for det in detections:
        cls_lower = det.get("class_name", "").lower()
        if cls_lower in HELMET_POSITIVE_CLASSES or cls_lower in HELMET_NEGATIVE_CLASSES or \
           cls_lower in VEST_POSITIVE_CLASSES or cls_lower in VEST_NEGATIVE_CLASSES:
            ppe_boxes.append(det)

    people_results = []
    helmet_detected_count = 0
    helmet_missing_count = 0
    vest_detected_count = 0
    vest_missing_count = 0
    uncertain_count = 0

    # Process each detected person
    for idx, person in enumerate(people, start=1):
        px1, py1, px2, py2 = person["x1"], person["y1"], person["x2"], person["y2"]
        p_w = px2 - px1
        p_h = py2 - py1

        # Head region (top 35% of person height)
        head_box = {"x1": px1, "y1": py1, "x2": px2, "y2": py1 + p_h * 0.35}
        # Torso region (20% to 75% of person height)
        torso_box = {"x1": px1, "y1": py1 + p_h * 0.20, "x2": px2, "y2": py1 + p_h * 0.75}

        best_helmet_conf = 0.0
        best_helmet_state = None  # True (pos), False (neg), or None

        best_vest_conf = 0.0
        best_vest_state = None

        # 1. Match against explicit PPE bounding boxes
        for ppe_det in ppe_boxes:
            cls_name = ppe_det.get("class_name", "").lower()
            conf = float(ppe_det.get("confidence", 0.0))

            # Bounding box center of PPE item
            cx = (ppe_det.get("x1", 0) + ppe_det.get("x2", 0)) / 2.0
            cy = (ppe_det.get("y1", 0) + ppe_det.get("y2", 0)) / 2.0
            center_point = (cx, cy)

            # Helmet check
            if cls_name in HELMET_POSITIVE_CLASSES:
                if is_point_in_box(center_point, head_box) or is_point_in_box(center_point, person):
                    if conf > best_helmet_conf:
                        best_helmet_conf = conf
                        best_helmet_state = True
            elif cls_name in HELMET_NEGATIVE_CLASSES:
                if is_point_in_box(center_point, head_box) or is_point_in_box(center_point, person):
                    if conf > best_helmet_conf:
                        best_helmet_conf = conf
                        best_helmet_state = False

            # Vest check
            if cls_name in VEST_POSITIVE_CLASSES:
                if is_point_in_box(center_point, torso_box) or is_point_in_box(center_point, person):
                    if conf > best_vest_conf:
                        best_vest_conf = conf
                        best_vest_state = True
            elif cls_name in VEST_NEGATIVE_CLASSES:
                if is_point_in_box(center_point, torso_box) or is_point_in_box(center_point, person):
                    if conf > best_vest_conf:
                        best_vest_conf = conf
                        best_vest_state = False

        # 2. If no explicit PPE bounding box was matched, attempt image ROI analysis if source image is provided
        if best_helmet_state is None and isinstance(source, np.ndarray):
            roi_res = analyze_person_roi_hsv(source, person)

            if best_helmet_state is None:
                h_score = roi_res["helmet_score"]
                h_conf = roi_res["helmet_confidence"]
                if h_conf >= confidence_threshold:
                    best_helmet_state = (h_score >= 0.5)
                    best_helmet_conf = h_conf
                else:
                    best_helmet_conf = h_conf

            if best_vest_state is None:
                v_score = roi_res["vest_score"]
                v_conf = roi_res["vest_confidence"]
                if v_conf >= confidence_threshold:
                    best_vest_state = (v_score >= 0.5)
                    best_vest_conf = v_conf
                else:
                    best_vest_conf = v_conf

        # 3. Determine final status & boolean values based on thresholds
        # Helmet status determination
        if best_helmet_conf >= confidence_threshold and best_helmet_state is not None:
            if best_helmet_state:
                helmet_detected = True
                helmet_status = "DETECTED"
                helmet_detected_count += 1
            else:
                helmet_detected = False
                helmet_status = "NOT_DETECTED"
                helmet_missing_count += 1
        else:
            # Below confidence_threshold or unmapped -> UNCERTAIN
            helmet_detected = None
            helmet_status = "UNCERTAIN"

        # Vest status determination
        if best_vest_conf >= confidence_threshold and best_vest_state is not None:
            if best_vest_state:
                vest_detected = True
                vest_status = "DETECTED"
                vest_detected_count += 1
            else:
                vest_detected = False
                vest_status = "NOT_DETECTED"
                vest_missing_count += 1
        else:
            # Below confidence_threshold or unmapped -> UNCERTAIN
            vest_detected = None
            vest_status = "UNCERTAIN"

        if helmet_status == "UNCERTAIN" or vest_status == "UNCERTAIN":
            uncertain_count += 1

        person_entry = {
            "person_id": idx,
            "box": [round(px1, 2), round(py1, 2), round(px2, 2), round(py2, 2)],
            "person_confidence": round(float(person.get("confidence", 1.0)), 2),
            "helmet_detected": helmet_detected,
            "helmet_confidence": round(best_helmet_conf, 2),
            "helmet_status": helmet_status,
            "vest_detected": vest_detected,
            "vest_confidence": round(best_vest_conf, 2),
            "vest_status": vest_status
        }
        people_results.append(person_entry)

    summary = {
        "people_count": len(people),
        "helmet_detected_count": helmet_detected_count,
        "helmet_missing_count": helmet_missing_count,
        "vest_detected_count": vest_detected_count,
        "vest_missing_count": vest_missing_count,
        "uncertain_count": uncertain_count
    }

    return {
        "people": people_results,
        "summary": summary,
        "confidence_threshold": confidence_threshold,
        "uncertainty_threshold": uncertainty_threshold,
        "model_note": (
            "Standard YOLOv8n (COCO) detects people/vehicles. "
            "PPE analysis evaluates secondary PPE detections / ROI features with explicit UNCERTAIN state handling."
        )
    }


if __name__ == "__main__":
    print("=== TESTING PPE DETECTOR MODULE ===")
    sample_people = [
        {"class_name": "person", "confidence": 0.95, "x1": 100, "y1": 100, "x2": 200, "y2": 400}
    ]
    sample_ppe = [
        {"class_name": "helmet", "confidence": 0.92, "x1": 120, "y1": 100, "x2": 180, "y2": 160},
        {"class_name": "vest", "confidence": 0.88, "x1": 110, "y1": 180, "x2": 190, "y2": 320}
    ]
    res = detect_ppe(detections=sample_people, custom_ppe_detections=sample_ppe)
    print("PPE Detection Result:")
    import json
    print(json.dumps(res, indent=2))
