"""
test_ppe.py - Comprehensive Test Suite for PPE (Helmet & Vest) Detection Engine

Test Scenarios Covered:
1. Full PPE Compliant Person (Helmet: True, Vest: True)
2. Non-Compliant Person (Helmet: False, Vest: False)
3. Partial PPE Compliant Person (Helmet: True, Vest: False)
4. Multiple People with Mixed Compliance (3 People)
5. Uncertain Detection (Low Confidence -> UNCERTAIN status without false missing flags)
6. No People Detected (Empty detections list)
"""

import sys
import json
from ppe_detector import detect_ppe, DEFAULT_CONFIDENCE_THRESHOLD, DEFAULT_UNCERTAINTY_THRESHOLD


def run_all_ppe_tests():
    print("=" * 65)
    print("RUNNING PPE (HELMET & SAFETY VEST) DETECTION TEST SUITE")
    print("=" * 65)

    passed_count = 0
    total_tests = 6

    # ---------------------------------------------------------
    # TEST 1: Full PPE Compliant Person
    # ---------------------------------------------------------
    print("\n--- TEST 1: Fully Compliant Worker (Helmet + Vest) ---")
    people_t1 = [
        {"class_name": "person", "confidence": 0.95, "x1": 100, "y1": 100, "x2": 200, "y2": 400}
    ]
    ppe_t1 = [
        {"class_name": "helmet", "confidence": 0.92, "x1": 120, "y1": 105, "x2": 180, "y2": 150},
        {"class_name": "vest", "confidence": 0.89, "x1": 110, "y1": 180, "x2": 190, "y2": 320}
    ]
    res1 = detect_ppe(detections=people_t1, custom_ppe_detections=ppe_t1)
    print("Result:")
    print(json.dumps(res1, indent=2))

    assert len(res1["people"]) == 1, "Expected 1 person result"
    p1 = res1["people"][0]
    assert p1["person_id"] == 1
    assert p1["helmet_detected"] is True
    assert p1["helmet_status"] == "DETECTED"
    assert p1["helmet_confidence"] == 0.92
    assert p1["vest_detected"] is True
    assert p1["vest_status"] == "DETECTED"
    assert p1["vest_confidence"] == 0.89

    summary1 = res1["summary"]
    assert summary1["people_count"] == 1
    assert summary1["helmet_detected_count"] == 1
    assert summary1["helmet_missing_count"] == 0
    assert summary1["vest_detected_count"] == 1
    assert summary1["vest_missing_count"] == 0
    assert summary1["uncertain_count"] == 0
    print("[PASS] Test 1 Succeeded!")
    passed_count += 1

    # ---------------------------------------------------------
    # TEST 2: Non-Compliant Person (Explicit Missing PPE)
    # ---------------------------------------------------------
    print("\n--- TEST 2: Non-Compliant Worker (No Helmet + No Vest) ---")
    people_t2 = [
        {"class_name": "person", "confidence": 0.91, "x1": 300, "y1": 100, "x2": 400, "y2": 400}
    ]
    ppe_t2 = [
        {"class_name": "no_helmet", "confidence": 0.87, "x1": 320, "y1": 105, "x2": 380, "y2": 150},
        {"class_name": "no_vest", "confidence": 0.84, "x1": 310, "y1": 180, "x2": 390, "y2": 320}
    ]
    res2 = detect_ppe(detections=people_t2, custom_ppe_detections=ppe_t2)
    print("Result:")
    print(json.dumps(res2, indent=2))

    p2 = res2["people"][0]
    assert p2["helmet_detected"] is False
    assert p2["helmet_status"] == "NOT_DETECTED"
    assert p2["helmet_confidence"] == 0.87
    assert p2["vest_detected"] is False
    assert p2["vest_status"] == "NOT_DETECTED"
    assert p2["vest_confidence"] == 0.84

    summary2 = res2["summary"]
    assert summary2["people_count"] == 1
    assert summary2["helmet_detected_count"] == 0
    assert summary2["helmet_missing_count"] == 1
    assert summary2["vest_detected_count"] == 0
    assert summary2["vest_missing_count"] == 1
    print("[PASS] Test 2 Succeeded!")
    passed_count += 1

    # ---------------------------------------------------------
    # TEST 3: Partial PPE Compliant Person (Helmet Present, Vest Missing)
    # ---------------------------------------------------------
    print("\n--- TEST 3: Partial Compliant Worker (Helmet Present, No Vest) ---")
    people_t3 = [
        {"class_name": "person", "confidence": 0.94, "x1": 500, "y1": 100, "x2": 600, "y2": 400}
    ]
    ppe_t3 = [
        {"class_name": "helmet", "confidence": 0.93, "x1": 520, "y1": 105, "x2": 580, "y2": 150},
        {"class_name": "no_vest", "confidence": 0.86, "x1": 510, "y1": 180, "x2": 590, "y2": 320}
    ]
    res3 = detect_ppe(detections=people_t3, custom_ppe_detections=ppe_t3)
    print("Result:")
    print(json.dumps(res3, indent=2))

    p3 = res3["people"][0]
    assert p3["helmet_detected"] is True
    assert p3["helmet_status"] == "DETECTED"
    assert p3["vest_detected"] is False
    assert p3["vest_status"] == "NOT_DETECTED"

    summary3 = res3["summary"]
    assert summary3["helmet_detected_count"] == 1
    assert summary3["helmet_missing_count"] == 0
    assert summary3["vest_detected_count"] == 0
    assert summary3["vest_missing_count"] == 1
    print("[PASS] Test 3 Succeeded!")
    passed_count += 1

    # ---------------------------------------------------------
    # TEST 4: Multiple People with Mixed Compliance
    # ---------------------------------------------------------
    print("\n--- TEST 4: Multiple People with Mixed Compliance ---")
    people_t4 = [
        {"class_name": "person", "confidence": 0.95, "x1": 100, "y1": 100, "x2": 200, "y2": 400}, # Person 1: Fully compliant
        {"class_name": "person", "confidence": 0.90, "x1": 400, "y1": 100, "x2": 500, "y2": 400}, # Person 2: Non-compliant
        {"class_name": "person", "confidence": 0.88, "x1": 700, "y1": 100, "x2": 800, "y2": 400}  # Person 3: Helmet only
    ]
    ppe_t4 = [
        # Person 1 items
        {"class_name": "helmet", "confidence": 0.91, "x1": 120, "y1": 105, "x2": 180, "y2": 150},
        {"class_name": "vest", "confidence": 0.88, "x1": 110, "y1": 180, "x2": 190, "y2": 320},
        # Person 2 items
        {"class_name": "no_helmet", "confidence": 0.85, "x1": 420, "y1": 105, "x2": 480, "y2": 150},
        {"class_name": "no_vest", "confidence": 0.82, "x1": 410, "y1": 180, "x2": 490, "y2": 320},
        # Person 3 items
        {"class_name": "helmet", "confidence": 0.94, "x1": 720, "y1": 105, "x2": 780, "y2": 150},
        {"class_name": "no_vest", "confidence": 0.80, "x1": 710, "y1": 180, "x2": 790, "y2": 320}
    ]
    res4 = detect_ppe(detections=people_t4, custom_ppe_detections=ppe_t4)
    print("Result:")
    print(json.dumps(res4, indent=2))

    assert len(res4["people"]) == 3
    summary4 = res4["summary"]
    assert summary4["people_count"] == 3
    assert summary4["helmet_detected_count"] == 2
    assert summary4["helmet_missing_count"] == 1
    assert summary4["vest_detected_count"] == 1
    assert summary4["vest_missing_count"] == 2
    print("[PASS] Test 4 Succeeded!")
    passed_count += 1

    # ---------------------------------------------------------
    # TEST 5: Uncertain Detection (Low Confidence -> UNCERTAIN status)
    # ---------------------------------------------------------
    print("\n--- TEST 5: Uncertain Detection (Low Confidence Handling) ---")
    people_t5 = [
        {"class_name": "person", "confidence": 0.70, "x1": 100, "y1": 100, "x2": 200, "y2": 400}
    ]
    # Low confidence PPE detections (below confidence_threshold=0.50)
    ppe_t5 = [
        {"class_name": "helmet", "confidence": 0.35, "x1": 120, "y1": 105, "x2": 180, "y2": 150},
        {"class_name": "vest", "confidence": 0.40, "x1": 110, "y1": 180, "x2": 190, "y2": 320}
    ]
    res5 = detect_ppe(detections=people_t5, custom_ppe_detections=ppe_t5, confidence_threshold=0.50)
    print("Result:")
    print(json.dumps(res5, indent=2))

    p5 = res5["people"][0]
    assert p5["helmet_detected"] is None, "Expected helmet_detected=None for uncertain detection"
    assert p5["helmet_status"] == "UNCERTAIN"
    assert p5["vest_detected"] is None, "Expected vest_detected=None for uncertain detection"
    assert p5["vest_status"] == "UNCERTAIN"

    summary5 = res5["summary"]
    assert summary5["uncertain_count"] == 1
    assert summary5["helmet_missing_count"] == 0, "Uncertain detection must NOT be claimed as confirmed missing"
    assert summary5["vest_missing_count"] == 0, "Uncertain detection must NOT be claimed as confirmed missing"
    print("[PASS] Test 5 Succeeded!")
    passed_count += 1

    # ---------------------------------------------------------
    # TEST 6: No People Detected
    # ---------------------------------------------------------
    print("\n--- TEST 6: No People Detected ---")
    detections_t6 = [
        {"class_name": "car", "confidence": 0.90, "x1": 100, "y1": 100, "x2": 300, "y2": 250}
    ]
    res6 = detect_ppe(detections=detections_t6)
    print("Result:")
    print(json.dumps(res6, indent=2))

    assert len(res6["people"]) == 0
    assert res6["summary"]["people_count"] == 0
    assert res6["summary"]["helmet_detected_count"] == 0
    assert res6["summary"]["helmet_missing_count"] == 0
    assert res6["summary"]["vest_detected_count"] == 0
    assert res6["summary"]["vest_missing_count"] == 0
    print("[PASS] Test 6 Succeeded!")
    passed_count += 1

    print("\n" + "=" * 65)
    print(f"SUMMARY: {passed_count}/{total_tests} PPE TESTS PASSED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == "__main__":
    run_all_ppe_tests()
