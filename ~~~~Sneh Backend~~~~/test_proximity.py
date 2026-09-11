"""
test_proximity.py - Test Suite for Upgraded Person-Vehicle Proximity Analysis

Tests all required scenarios:
1. Multiple people + one vehicle
2. One person + multiple vehicles
3. Multiple people + multiple vehicles
4. No vehicles
5. No people
"""

import sys
from proximity import check_person_vehicle_proximity, PROXIMITY_THRESHOLD


def run_all_tests():
    print("=" * 60)
    print("RUNNING PERSON-VEHICLE PROXIMITY TEST SUITE")
    print("=" * 60)

    passed_count = 0
    total_tests = 6

    # ---------------------------------------------------------
    # TEST 1: Multiple people + One vehicle
    # ---------------------------------------------------------
    print("\n--- TEST 1: Multiple People + One Vehicle ---")
    detections_t1 = [
        {"class_name": "person", "confidence": 0.92, "x1": 100, "y1": 100, "x2": 200, "y2": 300},  # center: (150, 200)
        {"class_name": "person", "confidence": 0.88, "x1": 800, "y1": 800, "x2": 900, "y2": 900},  # center: (850, 850)
        {"class_name": "car", "confidence": 0.85, "x1": 180, "y1": 120, "x2": 450, "y2": 350}       # center: (315, 235)
    ]
    res1 = check_person_vehicle_proximity(detections_t1)
    print(f"Number of People   : {res1['number_of_people']}")
    print(f"Number of Vehicles : {res1['number_of_vehicles']}")
    print(f"Closest Person     : {res1['closest_person']['center']}")
    print(f"Closest Vehicle    : {res1['closest_vehicle']['class_name']} at {res1['closest_vehicle']['center']}")
    print(f"Distance           : {res1['distance']} px")
    print(f"Person Near Vehicle: {res1['person_near_vehicle']}")
    print(f"Pairs Evaluated    : {len(res1['pairs'])}")
    print(f"Approximation Note : {res1['approximation_note']}")

    assert res1['number_of_people'] == 2, f"Expected 2 people, got {res1['number_of_people']}"
    assert res1['number_of_vehicles'] == 1, f"Expected 1 vehicle, got {res1['number_of_vehicles']}"
    assert res1['closest_person']['center'] == (150.0, 200.0), f"Unexpected closest person: {res1['closest_person']}"
    assert res1['closest_vehicle']['class_name'] == "car", f"Unexpected closest vehicle: {res1['closest_vehicle']}"
    assert res1['distance'] == 168.67, f"Expected distance 168.67, got {res1['distance']}"
    assert res1['person_near_vehicle'] is True, "Expected person_near_vehicle=True"
    assert len(res1['pairs']) == 2, f"Expected 2 pairs, got {len(res1['pairs'])}"
    print("[PASS] Test 1 Succeeded!")
    passed_count += 1

    # ---------------------------------------------------------
    # TEST 2: One person + Multiple vehicles
    # ---------------------------------------------------------
    print("\n--- TEST 2: One Person + Multiple Vehicles ---")
    detections_t2 = [
        {"class_name": "person", "confidence": 0.95, "x1": 100, "y1": 100, "x2": 200, "y2": 300},  # center: (150, 200)
        {"class_name": "bus", "confidence": 0.90, "x1": 800, "y1": 800, "x2": 950, "y2": 950},     # center: (875, 875)
        {"class_name": "truck", "confidence": 0.87, "x1": 180, "y1": 120, "x2": 450, "y2": 350}    # center: (315, 235)
    ]
    res2 = check_person_vehicle_proximity(detections_t2)
    print(f"Number of People   : {res2['number_of_people']}")
    print(f"Number of Vehicles : {res2['number_of_vehicles']}")
    print(f"Closest Person     : {res2['closest_person']['center']}")
    print(f"Closest Vehicle    : {res2['closest_vehicle']['class_name']} at {res2['closest_vehicle']['center']}")
    print(f"Distance           : {res2['distance']} px")
    print(f"Person Near Vehicle: {res2['person_near_vehicle']}")
    print(f"Pairs Evaluated    : {len(res2['pairs'])}")

    assert res2['number_of_people'] == 1, f"Expected 1 person, got {res2['number_of_people']}"
    assert res2['number_of_vehicles'] == 2, f"Expected 2 vehicles, got {res2['number_of_vehicles']}"
    assert res2['closest_vehicle']['class_name'] == "truck", f"Expected truck as closest, got {res2['closest_vehicle']['class_name']}"
    assert res2['distance'] == 168.67, f"Expected distance 168.67, got {res2['distance']}"
    assert res2['person_near_vehicle'] is True, "Expected person_near_vehicle=True"
    assert len(res2['pairs']) == 2, f"Expected 2 pairs, got {len(res2['pairs'])}"
    print("[PASS] Test 2 Succeeded!")
    passed_count += 1

    # ---------------------------------------------------------
    # TEST 3: Multiple people + Multiple vehicles
    # ---------------------------------------------------------
    print("\n--- TEST 3: Multiple People + Multiple Vehicles ---")
    detections_t3 = [
        {"class_name": "person", "confidence": 0.91, "x1": 100, "y1": 100, "x2": 200, "y2": 300},  # center: (150, 200)
        {"class_name": "person", "confidence": 0.89, "x1": 400, "y1": 400, "x2": 500, "y2": 500},  # center: (450, 450)
        {"class_name": "car", "confidence": 0.85, "x1": 160, "y1": 150, "x2": 240, "y2": 250},     # center: (200, 200)
        {"class_name": "bus", "confidence": 0.80, "x1": 700, "y1": 700, "x2": 900, "y2": 900}      # center: (800, 800)
    ]
    # Test with default threshold (200)
    res3 = check_person_vehicle_proximity(detections_t3, threshold=200)
    print(f"Number of People   : {res3['number_of_people']}")
    print(f"Number of Vehicles : {res3['number_of_vehicles']}")
    print(f"Closest Pair Dist  : {res3['distance']} px")
    print(f"Closest Person     : {res3['closest_person']['center']}")
    print(f"Closest Vehicle    : {res3['closest_vehicle']['class_name']} at {res3['closest_vehicle']['center']}")
    print(f"Person Near Vehicle (threshold=200): {res3['person_near_vehicle']}")
    print(f"Pairs Evaluated    : {len(res3['pairs'])}")

    # Also test configurable custom threshold (e.g. 40)
    res3_strict = check_person_vehicle_proximity(detections_t3, threshold=40)
    print(f"Person Near Vehicle (threshold=40) : {res3_strict['person_near_vehicle']}")

    assert res3['number_of_people'] == 2, f"Expected 2 people, got {res3['number_of_people']}"
    assert res3['number_of_vehicles'] == 2, f"Expected 2 vehicles, got {res3['number_of_vehicles']}"
    assert len(res3['pairs']) == 4, f"Expected 4 pair calculations, got {len(res3['pairs'])}"
    assert res3['distance'] == 50.0, f"Expected min distance 50.0, got {res3['distance']}"
    assert res3['closest_person']['center'] == (150.0, 200.0)
    assert res3['closest_vehicle']['class_name'] == "car"
    assert res3['person_near_vehicle'] is True, "Expected person_near_vehicle=True for threshold=200"
    assert res3_strict['person_near_vehicle'] is True, "Overlapping boxes should remain near despite center threshold"
    print("[PASS] Test 3 Succeeded!")
    passed_count += 1

    # ---------------------------------------------------------
    # TEST 4: No vehicles
    # ---------------------------------------------------------
    print("\n--- TEST 4: No Vehicles ---")
    detections_t4 = [
        {"class_name": "person", "confidence": 0.90, "x1": 100, "y1": 100, "x2": 200, "y2": 300},
        {"class_name": "person", "confidence": 0.88, "x1": 400, "y1": 400, "x2": 500, "y2": 500},
        {"class_name": "dog", "confidence": 0.75, "x1": 50, "y1": 50, "x2": 80, "y2": 80}
    ]
    res4 = check_person_vehicle_proximity(detections_t4)
    print(f"Number of People   : {res4['number_of_people']}")
    print(f"Number of Vehicles : {res4['number_of_vehicles']}")
    print(f"Closest Person     : {res4['closest_person']}")
    print(f"Closest Vehicle    : {res4['closest_vehicle']}")
    print(f"Distance           : {res4['distance']}")
    print(f"Person Near Vehicle: {res4['person_near_vehicle']}")
    print(f"Pairs Evaluated    : {len(res4['pairs'])}")

    assert res4['number_of_people'] == 2, f"Expected 2 people, got {res4['number_of_people']}"
    assert res4['number_of_vehicles'] == 0, f"Expected 0 vehicles, got {res4['number_of_vehicles']}"
    assert res4['closest_person'] is None, "Expected closest_person=None"
    assert res4['closest_vehicle'] is None, "Expected closest_vehicle=None"
    assert res4['distance'] is None, "Expected distance=None"
    assert res4['person_near_vehicle'] is False, "Expected person_near_vehicle=False"
    assert len(res4['pairs']) == 0, "Expected 0 pairs"
    print("[PASS] Test 4 Succeeded!")
    passed_count += 1

    # ---------------------------------------------------------
    # TEST 5: No people
    # ---------------------------------------------------------
    print("\n--- TEST 5: No People ---")
    detections_t5 = [
        {"class_name": "car", "confidence": 0.92, "x1": 100, "y1": 100, "x2": 300, "y2": 250},
        {"class_name": "motorcycle", "confidence": 0.86, "x1": 400, "y1": 400, "x2": 500, "y2": 500}
    ]
    res5 = check_person_vehicle_proximity(detections_t5)
    print(f"Number of People   : {res5['number_of_people']}")
    print(f"Number of Vehicles : {res5['number_of_vehicles']}")
    print(f"Closest Person     : {res5['closest_person']}")
    print(f"Closest Vehicle    : {res5['closest_vehicle']}")
    print(f"Distance           : {res5['distance']}")
    print(f"Person Near Vehicle: {res5['person_near_vehicle']}")
    print(f"Pairs Evaluated    : {len(res5['pairs'])}")

    assert res5['number_of_people'] == 0, f"Expected 0 people, got {res5['number_of_people']}"
    assert res5['number_of_vehicles'] == 2, f"Expected 2 vehicles, got {res5['number_of_vehicles']}"
    assert res5['closest_person'] is None, "Expected closest_person=None"
    assert res5['closest_vehicle'] is None, "Expected closest_vehicle=None"
    assert res5['distance'] is None, "Expected distance=None"
    assert res5['person_near_vehicle'] is False, "Expected person_near_vehicle=False"
    assert len(res5['pairs']) == 0, "Expected 0 pairs"
    print("[PASS] Test 5 Succeeded!")
    passed_count += 1

    # ---------------------------------------------------------
    # TEST 6: Overlapping large boxes must count as near
    # ---------------------------------------------------------
    print("\n--- TEST 6: Overlapping Boxes with Distant Centers ---")
    detections_t6 = [
        {"class_name": "person", "confidence": 0.90, "x1": 100, "y1": 100, "x2": 220, "y2": 700},
        {"class_name": "truck", "confidence": 0.90, "x1": 180, "y1": 80, "x2": 800, "y2": 760}
    ]
    res6 = check_person_vehicle_proximity(detections_t6, threshold=50)
    print(f"Center distance    : {res6['distance']} px")
    print(f"Box edge gap       : {res6['box_gap']} px")
    print(f"Person Near Vehicle: {res6['person_near_vehicle']}")

    assert res6['distance'] > 50, "This case should exceed the center threshold"
    assert res6['box_gap'] == 0, "Expected overlapping detection boxes"
    assert res6['person_near_vehicle'] is True, "Overlapping boxes must be considered near"
    print("[PASS] Test 6 Succeeded!")
    passed_count += 1

    print("\n" + "=" * 60)
    print(f"SUMMARY: {passed_count}/{total_tests} TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
