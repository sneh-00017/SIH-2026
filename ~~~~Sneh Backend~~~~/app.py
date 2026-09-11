import cv2
import numpy as np
import os
import tempfile
import base64
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from risk_engine import calculate_risk_from_flags
from detector import detect_objects_stub
from safety_pipeline import run_safety_pipeline
from database import initialize_database, list_analyses, save_analysis

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from the frontend dev server
initialize_database()
VIDEO_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "video_outputs")
os.makedirs(VIDEO_OUTPUT_DIR, exist_ok=True)

@app.route("/")
def home():
    return "AI Risk Detector Backend is running!"
@app.route("/api/health")
def health():
    return {
        "status": "ok",
        "message": "AI Risk Detector Backend is running!"
    }


@app.route("/api/analyses", methods=["GET"])
def analyses():
    return jsonify({"analyses": list_analyses()}), 200


@app.route("/api/video-output/<path:filename>", methods=["GET"])
def video_output(filename):
    mimetype = "video/webm" if filename.lower().endswith(".webm") else "video/mp4"
    return send_from_directory(VIDEO_OUTPUT_DIR, filename, mimetype=mimetype)

@app.route("/risk", methods=["POST", "GET"])
def calculate_risk():
    # 1. Get JSON payload from incoming request (default to empty dict if none provided)
    data = request.get_json(silent=True) or {}

    # 2. Compute risk using risk_engine module
    result = calculate_risk_from_flags(data)

    # 3. Return JSON result
    return jsonify(result)

@app.route("/detect", methods=["POST", "GET"])
def detect_and_assess_risk():
    """
    Endpoint that connects AI Object Detection (detector.py) 
    with Risk Scoring (risk_engine.py).
    """
    # 1. Get detections from detector module
    detection_result = detect_objects_stub()

    # 2. Pass hazard flags into risk engine module
    risk_result = calculate_risk_from_flags(detection_result["flags"])

    # 3. Return combined response
    return jsonify({
        "detections": detection_result["detections"],
        "hazard_flags": detection_result["flags"],
        "risk_assessment": risk_result
    })

@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Endpoint to process an uploaded image through the complete AI safety pipeline:
    Uploaded Image -> OpenCV Decode -> YOLO Detector -> Proximity Engine -> Hazard Flags -> Risk Engine
    """
    # 1. Check whether an image file was uploaded
    if 'image' not in request.files and 'file' not in request.files:
        return jsonify({"error": "No image file provided in request. Use 'image' or 'file' form field."}), 400

    file = request.files.get('image') or request.files.get('file')
    if not file or file.filename == '':
        return jsonify({"error": "No selected image file."}), 400

    # 2. Read file bytes and decode into OpenCV image frame
    try:
        file_bytes = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if image is None:
            return jsonify({"error": "Invalid image file. Could not decode image."}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to read image file: {str(e)}"}), 400

    # 3. Run safety pipeline
    try:
        pipeline_res = run_safety_pipeline(image)
        flags = pipeline_res.get("flags", {})
        risk = pipeline_res.get("risk_assessment", {})

        response = {
            "detected_objects": pipeline_res.get("detections", []),
            "person_detected": flags.get("person_detected", False),
            "vehicle_detected": flags.get("vehicle_detected", False),
            "person_near_vehicle": flags.get("person_near_vehicle", False),
            "risk_score": risk.get("risk_score", 0),
            "score": risk.get("score", 0),
            "risk": risk.get("risk_level", "LOW"),
            "risk_level": risk.get("risk_level", "LOW"),
            "hazards": risk.get("hazards", []),
            "explanation": risk.get("explanation", []),
            "risk_factors": risk.get("risk_factors", []),
            "score_basis": risk.get("score_basis", {}),
            "disclaimer": risk.get("disclaimer", ""),
            "proximity_details": pipeline_res.get("proximity_details", {}),
            "ppe_details": pipeline_res.get("ppe_details", {})
        }
        response["analysis_id"] = save_analysis(
            response,
            "image",
            file.filename,
            metadata={"proximity_details": pipeline_res.get("proximity_details", {}), "ppe_details": pipeline_res.get("ppe_details", {})},
        )
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Error during image risk analysis: {str(e)}"}), 500


@app.route("/analyze-video", methods=["POST"])
def analyze_video():
    """Sample an uploaded video and return the highest observed safety risk."""
    file = request.files.get("video") or request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "No video file provided."}), 400

    temp_path = None
    capture = None
    writer = None
    output_filename = f"analysis-{uuid.uuid4().hex}.webm"
    output_path = os.path.join(VIDEO_OUTPUT_DIR, output_filename)
    try:
        suffix = os.path.splitext(file.filename)[1] or ".mp4"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            file.save(temp_file)
            temp_path = temp_file.name

        capture = cv2.VideoCapture(temp_path)
        if not capture.isOpened():
            return jsonify({"error": "The uploaded video could not be opened."}), 400

        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        fps = capture.get(cv2.CAP_PROP_FPS) or 1
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"VP80"), fps, (width, height))
        if not writer.isOpened():
            writer.release()
            output_filename = f"analysis-{uuid.uuid4().hex}.mp4"
            output_path = os.path.join(VIDEO_OUTPUT_DIR, output_filename)
            writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
        if not writer.isOpened():
            return jsonify({"error": "The annotated video output could not be created."}), 500
        sample_step = max(1, int(fps * 0.5))
        best_result = None
        best_frame_image = None
        evidence_frames = []
        evidence_states = set()
        frame_timeline = []
        sampled_frames = 0
        frame_index = 0
        previous_gray = None
        current_detections = []
        current_status = "clear"
        current_border = (150, 150, 150)

        while True:
            success, frame = capture.read()
            if not success:
                break
            if frame_index % sample_step == 0:
                pipeline_res = run_safety_pipeline(frame)
                risk = pipeline_res.get("risk_assessment", {})
                detections = pipeline_res.get("detections", [])
                flags = pipeline_res.get("flags", {})
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                motion_score = 0.0
                if previous_gray is not None:
                    difference = cv2.absdiff(previous_gray, gray)
                    motion_score = round(float(np.mean(difference)) / 255 * 100, 2)
                previous_gray = gray
                risk_score = risk.get("risk_score", 0)
                has_person = flags.get("person_detected", False)
                motion_alert = motion_score >= 12 and (has_person or flags.get("vehicle_detected", False))
                is_danger = risk_score > 0 or flags.get("person_near_vehicle", False) or motion_alert
                frame_status = "danger" if is_danger else "person" if has_person else "clear"
                relevant_detections = [
                    detection for detection in detections
                    if detection.get("class_name", "").lower() in {"person", "car", "truck", "bus", "motorcycle", "bicycle"}
                ]
                current_detections = relevant_detections
                current_status = frame_status
                current_border = (40, 40, 235) if is_danger else (70, 215, 105) if has_person else (150, 150, 150)
                annotated = frame.copy()
                border_color = (40, 40, 235) if is_danger else (70, 215, 105) if has_person else (150, 150, 150)
                for detection in relevant_detections:
                    x1 = int(detection.get("x1", 0))
                    y1 = int(detection.get("y1", 0))
                    x2 = int(detection.get("x2", 0))
                    y2 = int(detection.get("y2", 0))
                    color = (40, 40, 235) if is_danger else (70, 215, 105) if detection.get("class_name", "").lower() == "person" else border_color
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 3)
                    label = f"{detection.get('class_name', 'object')} {float(detection.get('confidence', 0)):.0%}"
                    cv2.putText(annotated, label, (x1, max(22, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                height, width = annotated.shape[:2]
                cv2.rectangle(annotated, (6, 6), (width - 7, height - 7), border_color, 14)
                ok, encoded = cv2.imencode(".jpg", annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 82])
                evidence_image = base64.b64encode(encoded).decode("ascii") if ok else None
                candidate = {
                    "risk_score": risk_score,
                    "score": risk.get("score", 0),
                    "risk_level": risk.get("risk_level", "LOW"),
                    "hazards": risk.get("hazards", []),
                    "explanation": risk.get("explanation", []),
                    "risk_factors": risk.get("risk_factors", []),
                    "score_basis": risk.get("score_basis", {}),
                    "detected_objects": relevant_detections,
                    "person_detected": has_person,
                    "vehicle_detected": flags.get("vehicle_detected", False),
                    "person_near_vehicle": flags.get("person_near_vehicle", False),
                    "disclaimer": risk.get("disclaimer", ""),
                    "motion_score": motion_score,
                    "motion_alert": motion_alert,
                    "frame_status": frame_status,
                    "frame_number": frame_index,
                    "evidence_priority": (2 if is_danger else 1 if has_person else 0, risk_score, motion_score),
                }
                if len(frame_timeline) < 40:
                    frame_timeline.append({
                        "frame_number": frame_index,
                        "risk_score": risk_score,
                        "motion_score": motion_score,
                        "status": frame_status,
                        "has_person": has_person,
                    })
                if evidence_image and (len(evidence_frames) < 18 or frame_status not in evidence_states):
                    evidence_frames.append({
                        "frame_number": frame_index,
                        "status": frame_status,
                        "risk_score": risk_score,
                        "motion_score": motion_score,
                        "image": f"data:image/jpeg;base64,{evidence_image}",
                    })
                    evidence_states.add(frame_status)
                if best_result is None or candidate["evidence_priority"] > best_result["evidence_priority"]:
                    best_result = candidate
                    best_frame_image = evidence_image
                sampled_frames += 1
            output_frame = frame.copy()
            for detection in current_detections:
                x1 = int(detection.get("x1", 0))
                y1 = int(detection.get("y1", 0))
                x2 = int(detection.get("x2", 0))
                y2 = int(detection.get("y2", 0))
                box_color = (40, 40, 235) if current_status == "danger" else (70, 215, 105) if detection.get("class_name", "").lower() == "person" else current_border
                cv2.rectangle(output_frame, (x1, y1), (x2, y2), box_color, 3)
            cv2.rectangle(output_frame, (6, 6), (width - 7, height - 7), current_border, 14)
            writer.write(output_frame)
            frame_index += 1

        if best_result is None:
            return jsonify({"error": "No readable frames were found in the video."}), 400
        best_result["sampled_frames"] = sampled_frames
        best_result["video_frames"] = frame_count
        best_result["frame_timeline"] = frame_timeline
        best_result["evidence_frame"] = f"data:image/jpeg;base64,{best_frame_image}" if best_frame_image else None
        best_result["evidence_frames"] = evidence_frames
        best_result["output_video_url"] = f"/api/video-output/{output_filename}"
        best_result["output_video_filename"] = output_filename
        best_result.pop("evidence_priority", None)
        best_result["analysis_id"] = save_analysis(
            best_result,
            "video",
            file.filename,
            metadata={"sampled_frames": sampled_frames, "video_frames": frame_count},
        )
        return jsonify(best_result), 200
    except Exception as error:
        return jsonify({"error": f"Error during video risk analysis: {error}"}), 500
    finally:
        if capture is not None:
            capture.release()
        if writer is not None:
            writer.release()
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)