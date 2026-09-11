"""
safety_pipeline.py - Integrated Safety Pipeline Module

This module connects AI object detection (detector.py), proximity evaluation
(proximity.py), and safety risk scoring (risk_engine.py) into a unified pipeline.

Pipeline Flow:
Image/Frame -> detector.py -> proximity.py -> Safety Flags -> risk_engine.py -> Final Risk Assessment

DISCLAIMER:
This score is a prototype heuristic indicator for demonstration purposes and does NOT
represent a calibrated real-world statistical probability of injury or fatality.
"""

from detector import detect_objects
from proximity import check_person_vehicle_proximity, VEHICLE_CLASSES
from risk_engine import calculate_risk_from_flags
from ppe_detector import detect_ppe


def run_safety_pipeline(source) -> dict:
    """
    Executes the full safety analysis pipeline on an image path or numpy frame.

    :param source: Image file path (str) or OpenCV frame (numpy ndarray).
    :return: A dictionary containing detections, proximity evaluation, ppe evaluation,
             hazard flags, and the calculated risk assessment.
    """
    # Step 1: Detect objects using YOLO
    detections = detect_objects(source)

    # Step 2: Determine basic presence flags
    person_detected = any(
        d.get("class_name", "").lower() == "person" for d in detections
    )
    vehicle_detected = any(
        d.get("class_name", "").lower() in VEHICLE_CLASSES for d in detections
    )

    # Step 3: Evaluate person-vehicle proximity
    proximity_result = check_person_vehicle_proximity(detections)
    person_near_vehicle = proximity_result.get("person_near_vehicle", False)

    # Step 4: Evaluate PPE compliance for detected people
    ppe_result = detect_ppe(source=source, detections=detections)
    ppe_summary = ppe_result.get("summary", {})

    # Extract PPE missing flags across all workers (uncertain status is NOT counted as missing)
    helmet_missing = ppe_summary.get("helmet_missing_count", 0) > 0
    safety_vest_missing = ppe_summary.get("vest_missing_count", 0) > 0

    # Step 5: Construct safety flags for the risk engine
    flags = {
        "person_detected": person_detected,
        "vehicle_detected": vehicle_detected,
        "person_near_vehicle": person_near_vehicle,
        "helmet_missing": helmet_missing,
        "safety_vest_missing": safety_vest_missing,
        "restricted_zone": False,
        "fall_detected": False
    }

    # Step 6: Calculate risk score & risk level via risk_engine
    risk_assessment = calculate_risk_from_flags(flags)

    # Step 7: Return integrated pipeline result
    return {
        "detections": detections,
        "detections_count": len(detections),
        "flags": flags,
        "proximity_details": proximity_result,
        "ppe_details": ppe_result,
        "risk_assessment": risk_assessment
    }


if __name__ == "__main__":
    print("=== TESTING INTEGRATED SAFETY PIPELINE ===")

    # Test 1: Real test using existing test.jpg
    image_path = "test.jpg"
    print(f"\n[Test 1] Real Image Pipeline Test ({image_path}):")
    res1 = run_safety_pipeline(image_path)
    print(f"Total Detections  : {res1['detections_count']}")
    print(f"Safety Flags      : {res1['flags']}")
    print(f"Proximity Details : {res1['proximity_details']}")
    print(f"Risk Assessment   : {res1['risk_assessment']}")

    # Test 2: Mock Detection Test (Person + Car in close proximity)
    print("\n[Test 2] Mock Detection Test (Person near Car):")
    mock_detections = [
        {"class_name": "person", "confidence": 0.95, "x1": 100, "y1": 100, "x2": 200, "y2": 300},
        {"class_name": "car", "confidence": 0.89, "x1": 180, "y1": 120, "x2": 450, "y2": 350}
    ]
    # Evaluate flags & risk directly from detections list
    person_detected = any(d.get("class_name", "").lower() == "person" for d in mock_detections)
    vehicle_detected = any(d.get("class_name", "").lower() in VEHICLE_CLASSES for d in mock_detections)
    prox_res = check_person_vehicle_proximity(mock_detections)
    mock_flags = {
        "person_detected": person_detected,
        "vehicle_detected": vehicle_detected,
        "person_near_vehicle": prox_res.get("person_near_vehicle", False),
        "helmet_missing": False,
        "safety_vest_missing": False,
        "restricted_zone": False,
        "fall_detected": False
    }
    mock_risk = calculate_risk_from_flags(mock_flags)
    print(f"Safety Flags      : {mock_flags}")
    print(f"Proximity Details : {prox_res}")
    print(f"Risk Assessment   : {mock_risk}")

