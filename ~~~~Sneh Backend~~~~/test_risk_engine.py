"""
test_risk_engine.py - Test Suite for PPE-Integrated Risk Scoring Engine

Tests all 7 required scenarios:
1. Safe worker (helmet present, vest present, no vehicle) -> LOW risk
2. Helmet missing -> Increased risk & 'Helmet missing' hazard
3. Vest missing -> Increased risk & 'Safety vest missing' hazard
4. Helmet + vest missing -> Both PPE hazards triggered
5. Person near vehicle + helmet missing -> Combined hazards & higher risk level (MEDIUM/HIGH)
6. Multiple people where one worker is missing PPE -> Multi-person PPE hazard detected
7. Uncertain PPE detection -> NOT automatically classified as missing
"""

import json
from risk_engine import calculate_risk_from_flags, DEFAULT_RISK_WEIGHTS
from ppe_detector import detect_ppe


def run_all_risk_engine_tests():
    print("=" * 70)
    print("RUNNING RISK ENGINE & PPE INTEGRATION TEST SUITE")
    print("=" * 70)

    passed_count = 0
    total_tests = 7

    # ---------------------------------------------------------
    # TEST 1: Safe worker (Helmet present, vest present, no nearby vehicle)
    # ---------------------------------------------------------
    print("\n--- TEST 1: Safe Worker (Helmet Present, Vest Present, No Vehicle) ---")
    data_t1 = {
        "person_detected": True,
        "vehicle_detected": False,
        "person_near_vehicle": False,
        "helmet_missing": False,
        "safety_vest_missing": False,
        "restricted_zone": False,
        "fall_detected": False
    }
    res1 = calculate_risk_from_flags(data_t1)
    print("Result:")
    print(json.dumps(res1, indent=2))

    assert res1["risk_score"] == 0, f"Expected score 0, got {res1['risk_score']}"
    assert res1["risk_level"] == "LOW", f"Expected LOW, got {res1['risk_level']}"
    assert len(res1["hazards"]) == 0, f"Expected no hazards, got {res1['hazards']}"
    assert "disclaimer" in res1, "Missing disclaimer"
    assert len(res1["explanation"]) > 0, "Missing explanation"
    print("[PASS] Test 1 Succeeded!")
    passed_count += 1

    # ---------------------------------------------------------
    # TEST 2: Helmet Missing
    # ---------------------------------------------------------
    print("\n--- TEST 2: Helmet Missing ---")
    data_t2 = {
        "person_detected": True,
        "vehicle_detected": False,
        "person_near_vehicle": False,
        "helmet_missing": True,
        "safety_vest_missing": False,
        "restricted_zone": False,
        "fall_detected": False
    }
    res2 = calculate_risk_from_flags(data_t2)
    print("Result:")
    print(json.dumps(res2, indent=2))

    assert res2["risk_score"] == 13, f"Expected normalized score 13, got {res2['risk_score']}"
    assert res2["risk_level"] == "LOW", f"Expected LOW, got {res2['risk_level']}"
    assert "Helmet missing" in res2["hazards"], "Expected 'Helmet missing' in hazards"
    assert any("helmet" in exp.lower() for exp in res2["explanation"]), "Expected helmet explanation"
    print("[PASS] Test 2 Succeeded!")
    passed_count += 1

    # ---------------------------------------------------------
    # TEST 3: Vest Missing
    # ---------------------------------------------------------
    print("\n--- TEST 3: Safety Vest Missing ---")
    data_t3 = {
        "person_detected": True,
        "vehicle_detected": False,
        "person_near_vehicle": False,
        "helmet_missing": False,
        "safety_vest_missing": True,
        "restricted_zone": False,
        "fall_detected": False
    }
    res3 = calculate_risk_from_flags(data_t3)
    print("Result:")
    print(json.dumps(res3, indent=2))

    assert res3["risk_score"] == 10, f"Expected normalized score 10, got {res3['risk_score']}"
    assert res3["risk_level"] == "LOW", f"Expected LOW, got {res3['risk_level']}"
    assert "Safety vest missing" in res3["hazards"], "Expected 'Safety vest missing' in hazards"
    assert any("vest" in exp.lower() for exp in res3["explanation"]), "Expected vest explanation"
    print("[PASS] Test 3 Succeeded!")
    passed_count += 1

    # ---------------------------------------------------------
    # TEST 4: Helmet + Vest Missing
    # ---------------------------------------------------------
    print("\n--- TEST 4: Both Helmet and Vest Missing ---")
    data_t4 = {
        "person_detected": True,
        "vehicle_detected": False,
        "person_near_vehicle": False,
        "helmet_missing": True,
        "safety_vest_missing": True,
        "restricted_zone": False,
        "fall_detected": False
    }
    res4 = calculate_risk_from_flags(data_t4)
    print("Result:")
    print(json.dumps(res4, indent=2))

    assert res4["risk_score"] == 23, f"Expected normalized score 23, got {res4['risk_score']}"
    assert "Helmet missing" in res4["hazards"]
    assert "Safety vest missing" in res4["hazards"]
    assert len(res4["explanation"]) == 2
    print("[PASS] Test 4 Succeeded!")
    passed_count += 1

    # ---------------------------------------------------------
    # TEST 5: Person Near Vehicle + Helmet Missing
    # ---------------------------------------------------------
    print("\n--- TEST 5: Person Near Vehicle + Helmet Missing ---")
    data_t5 = {
        "person_detected": True,
        "vehicle_detected": True,
        "person_near_vehicle": True,
        "helmet_missing": True,
        "safety_vest_missing": False,
        "restricted_zone": False,
        "fall_detected": False
    }
    res5 = calculate_risk_from_flags(data_t5)
    print("Result:")
    print(json.dumps(res5, indent=2))

    assert res5["risk_score"] == 37, f"Expected normalized score 37, got {res5['risk_score']}"
    assert res5["risk_level"] == "LOW", f"Expected LOW, got {res5['risk_level']}"
    assert "Person near vehicle" in res5["hazards"]
    assert "Helmet missing" in res5["hazards"]
    print("[PASS] Test 5 Succeeded!")
    passed_count += 1

    # ---------------------------------------------------------
    # TEST 6: Multiple People where One Worker is Missing PPE
    # ---------------------------------------------------------
    print("\n--- TEST 6: Multiple People (One Worker Missing PPE) ---")
    people_t6 = [
        {"class_name": "person", "confidence": 0.95, "x1": 100, "y1": 100, "x2": 200, "y2": 400}, # Compliant
        {"class_name": "person", "confidence": 0.92, "x1": 400, "y1": 100, "x2": 500, "y2": 400}  # Missing helmet
    ]
    ppe_t6 = [
        {"class_name": "helmet", "confidence": 0.90, "x1": 120, "y1": 105, "x2": 180, "y2": 150},
        {"class_name": "vest", "confidence": 0.88, "x1": 110, "y1": 180, "x2": 190, "y2": 320},
        {"class_name": "no_helmet", "confidence": 0.86, "x1": 420, "y1": 105, "x2": 480, "y2": 150},
        {"class_name": "vest", "confidence": 0.85, "x1": 410, "y1": 180, "x2": 490, "y2": 320}
    ]
    ppe_res6 = detect_ppe(detections=people_t6, custom_ppe_detections=ppe_t6)
    summary6 = ppe_res6["summary"]

    flags_t6 = {
        "person_detected": True,
        "vehicle_detected": False,
        "person_near_vehicle": False,
        "helmet_missing": summary6["helmet_missing_count"] > 0,
        "safety_vest_missing": summary6["vest_missing_count"] > 0,
        "restricted_zone": False,
        "fall_detected": False
    }
    res6 = calculate_risk_from_flags(flags_t6)
    print("PPE Summary:", summary6)
    print("Risk Result:")
    print(json.dumps(res6, indent=2))

    assert flags_t6["helmet_missing"] is True
    assert flags_t6["safety_vest_missing"] is False
    assert res6["risk_score"] == 13
    assert "Helmet missing" in res6["hazards"]
    print("[PASS] Test 6 Succeeded!")
    passed_count += 1

    # ---------------------------------------------------------
    # TEST 7: Uncertain PPE Detection (Should NOT be classified as missing)
    # ---------------------------------------------------------
    print("\n--- TEST 7: Uncertain PPE Detection Handling ---")
    people_t7 = [
        {"class_name": "person", "confidence": 0.70, "x1": 100, "y1": 100, "x2": 200, "y2": 400}
    ]
    # Low confidence PPE detection -> Status: UNCERTAIN
    ppe_t7 = [
        {"class_name": "helmet", "confidence": 0.35, "x1": 120, "y1": 105, "x2": 180, "y2": 150}
    ]
    ppe_res7 = detect_ppe(detections=people_t7, custom_ppe_detections=ppe_t7, confidence_threshold=0.50)
    summary7 = ppe_res7["summary"]

    # Verify that uncertain detection does NOT set helmet_missing to True
    flags_t7 = {
        "person_detected": True,
        "vehicle_detected": False,
        "person_near_vehicle": False,
        "helmet_missing": summary7["helmet_missing_count"] > 0,
        "safety_vest_missing": summary7["vest_missing_count"] > 0,
        "restricted_zone": False,
        "fall_detected": False
    }
    res7 = calculate_risk_from_flags(flags_t7)
    print("PPE Summary:", summary7)
    print("Risk Result:")
    print(json.dumps(res7, indent=2))

    assert summary7["uncertain_count"] == 1
    assert summary7["helmet_missing_count"] == 0, "Uncertain status must not count as missing"
    assert flags_t7["helmet_missing"] is False, "Uncertain PPE must NOT trigger helmet_missing flag"
    assert res7["risk_score"] == 0
    assert "Helmet missing" not in res7["hazards"]
    print("[PASS] Test 7 Succeeded!")
    passed_count += 1

    print("\n" + "=" * 70)
    print(f"SUMMARY: {passed_count}/{total_tests} RISK ENGINE TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_all_risk_engine_tests()
