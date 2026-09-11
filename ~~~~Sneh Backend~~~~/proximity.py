"""
proximity.py - Person + Vehicle Proximity Detection Module

This module checks whether detected people are dangerously close to vehicles
(cars, motorcycles, buses, trucks) based on bounding box center points.

========================================
BEGINNER EXPLANATION OF CONCEPTS:
========================================
1. BOUNDING BOXES (x1, y1, x2, y2):
   - A bounding box is a rectangular box enclosing a detected object in an image.
   - (x1, y1) represents the Top-Left corner pixel coordinates.
   - (x2, y2) represents the Bottom-Right corner pixel coordinates.

2. CENTER POINTS:
   - To measure object positions, we calculate the midpoint (center point) of each box:
       center_x = (x1 + x2) / 2
       center_y = (y1 + y2) / 2

3. DISTANCE CALCULATION:
   - We use the 2D Euclidean Distance formula to calculate straight-line pixel distance
     between a person's center point (px, py) and a vehicle's center point (vx, vy):
       distance = sqrt((px - vx)^2 + (py - vy)^2)

4. WHY PIXEL DISTANCE IS ONLY A PROTOTYPE APPROXIMATION:
   - Pixel distance is NOT real-world physical distance (e.g., meters or feet).
   - Perspective Distortion: Objects far from the camera look small and close in pixels,
     whereas objects near the camera take up many more pixels.
   - Lack of 3D Depth: A 2D image flattens 3D space, losing depth information (Z-axis).
   - Camera Angle & Resolution: Different camera positions and resolutions change pixel counts.
   - Therefore, threshold = 200 pixels is a heuristic PROTOTYPE rule for initial testing.
"""

import math

# Configurable prototype threshold (in pixels)
PROXIMITY_THRESHOLD = 200

# Vehicle classes from standard YOLO COCO dataset
VEHICLE_CLASSES = {"car", "motorcycle", "bus", "truck"}


def calculate_center(box: dict) -> tuple:
    """
    Calculates the center (x, y) coordinates of a bounding box dictionary.

    :param box: Dictionary containing 'x1', 'y1', 'x2', 'y2'
    :return: (center_x, center_y) tuple of floats
    """
    center_x = (box["x1"] + box["x2"]) / 2.0
    center_y = (box["y1"] + box["y2"]) / 2.0
    return (center_x, center_y)


def calculate_box_gap(first_box: dict, second_box: dict) -> float:
    """Return the shortest edge-to-edge distance between two detection boxes."""
    horizontal_gap = max(
        first_box["x1"] - second_box["x2"],
        second_box["x1"] - first_box["x2"],
        0,
    )
    vertical_gap = max(
        first_box["y1"] - second_box["y2"],
        second_box["y1"] - first_box["y2"],
        0,
    )
    return math.sqrt(horizontal_gap ** 2 + vertical_gap ** 2)


# Explicit Prototype Approximation Disclaimer
APPROXIMATION_NOTE = (
    "PROTOTYPE APPROXIMATION: Distance is measured in 2D image pixels, "
    "not 3D real-world physical units (meters/feet)."
)


def check_person_vehicle_proximity(detections: list, threshold: float = PROXIMITY_THRESHOLD) -> dict:
    """
    Determines pairwise proximity for all detected people and vehicles.

    :param detections: List of detection dicts returned by detector.py
                       (each containing 'class_name', 'x1', 'y1', 'x2', 'y2')
    :param threshold: Pixel distance threshold to consider as 'near' (default: 200)
    :return: Dictionary containing proximity information:
             - "person_near_vehicle": bool
             - "number_of_people": int
             - "number_of_vehicles": int
             - "closest_person": dict or None
             - "closest_vehicle": dict or None
             - "nearest_vehicle": str or None (class name of closest vehicle, preserved for backward compatibility)
             - "distance": float or None
             - "pairs": list of dicts with pair distance evaluations
             - "approximation_note": str
    """
    # 1. Find all detected people and vehicles
    people = []
    vehicles = []

    for det in detections:
        cls_name = det.get("class_name", "").lower()
        if cls_name == "person":
            people.append(det)
        elif cls_name in VEHICLE_CLASSES:
            vehicles.append(det)

    num_people = len(people)
    num_vehicles = len(vehicles)

    # If no people or no vehicles detected, return negative result with counts
    if not people or not vehicles:
        return {
            "person_near_vehicle": False,
            "number_of_people": num_people,
            "number_of_vehicles": num_vehicles,
            "closest_person": None,
            "closest_vehicle": None,
            "nearest_vehicle": None,
            "distance": None,
            "box_gap": None,
            "pairs": [],
            "approximation_note": APPROXIMATION_NOTE
        }

    # 2. Check every relevant person-vehicle pair & find closest/highest-risk pair
    min_distance = float("inf")
    closest_p = None
    closest_v = None
    evaluated_pairs = []

    for person in people:
        px, py = calculate_center(person)
        person_info = {**person, "center": (round(px, 2), round(py, 2))}

        for vehicle in vehicles:
            vx, vy = calculate_center(vehicle)
            vehicle_info = {**vehicle, "center": (round(vx, 2), round(vy, 2))}

            # Calculate Euclidean distance between center points
            dist = math.sqrt((px - vx) ** 2 + (py - vy) ** 2)
            dist_rounded = round(dist, 2)
            box_gap = calculate_box_gap(person, vehicle)
            is_pair_near = box_gap == 0 or dist <= threshold

            pair_entry = {
                "person": person_info,
                "vehicle": vehicle_info,
                "distance": dist_rounded,
                "box_gap": round(box_gap, 2),
                "near": is_pair_near
            }
            evaluated_pairs.append(pair_entry)

            if dist < min_distance:
                min_distance = dist
                closest_p = person_info
                closest_v = vehicle_info

    min_distance_rounded = round(min_distance, 2)
    closest_box_gap = calculate_box_gap(closest_p, closest_v) if closest_p and closest_v else None
    is_near = closest_box_gap == 0 or min_distance <= threshold
    nearest_vehicle_class = closest_v.get("class_name") if closest_v else None

    return {
        "person_near_vehicle": is_near,
        "number_of_people": num_people,
        "number_of_vehicles": num_vehicles,
        "closest_person": closest_p,
        "closest_vehicle": closest_v,
        "nearest_vehicle": nearest_vehicle_class,
        "distance": min_distance_rounded,
        "box_gap": round(closest_box_gap, 2) if closest_box_gap is not None else None,
        "pairs": evaluated_pairs,
        "approximation_note": APPROXIMATION_NOTE
    }


if __name__ == "__main__":
    print("=== TESTING PROXIMITY MODULE ===")

    # Test 1: Multiple people + single vehicle
    sample_detections = [
        {"class_name": "person", "confidence": 0.9, "x1": 100, "y1": 100, "x2": 200, "y2": 300},
        {"class_name": "person", "confidence": 0.85, "x1": 500, "y1": 500, "x2": 600, "y2": 700},
        {"class_name": "car", "confidence": 0.85, "x1": 180, "y1": 120, "x2": 450, "y2": 350},
        {"class_name": "dog", "confidence": 0.7, "x1": 10, "y1": 10, "x2": 50, "y2": 50}
    ]
    res1 = check_person_vehicle_proximity(sample_detections)
    print("\n[Test 1] Multi-person Sample:")
    print(res1)

    # Test 2: Hard-coded example list with a person far from a bus
    far_detections = [
        {"class_name": "person", "confidence": 0.9, "x1": 50, "y1": 50, "x2": 100, "y2": 150},
        {"class_name": "bus", "confidence": 0.88, "x1": 700, "y1": 700, "x2": 950, "y2": 900}
    ]
    res2 = check_person_vehicle_proximity(far_detections)
    print("\n[Test 2] Hard-coded Far Sample:")
    print(res2)

    # Test 3: Real detector output on test.jpg
    try:
        from detector import detect_objects
        print("\n[Test 3] Real test using detector.py on test.jpg:")
        real_detections = detect_objects("test.jpg")
        print(f"Detector found {len(real_detections)} object(s).")
        res3 = check_person_vehicle_proximity(real_detections)
        print("Proximity result:")
        print(res3)
    except Exception as e:
        print(f"\n[Test 3] Real detection test failed with error: {e}")

