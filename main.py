import cv2
import face_recognition
import time
import requests
from datetime import datetime
import os

from face_detection import load_known_faces, check_face_quality
from motion_detection import detect_motion
from alert_system import take_snapshot, send_alert_in_background

print("🔄 Initializing surveillance system...")

# Initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Error: Camera not accessible!")
    exit()
print("📸 Camera initialized successfully.")

# Ensure snapshots folder exists
SNAPSHOT_DIR = "snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

FLASK_SERVER = "http://127.0.0.1:5001/status"

# Initialize tracking variables
unknown_start_time = datetime.now()
sent_alerts = set()
prev_frame = None

# Load known face encodings
known_face_encodings, known_face_names = load_known_faces()

print("🚀 Surveillance system is now running...")
cv2.namedWindow("Surveillance Camera", cv2.WINDOW_NORMAL)

def is_surveillance_active():
    try:
        response = requests.get(FLASK_SERVER, timeout=3)
        return response.status_code == 200 and response.json().get("running", True)
    except:
        return True

while True:
    if not is_surveillance_active():
        print("🚨 Surveillance Stopped. Exiting...")
        break

    ret, frame = cap.read()
    if not ret:
        print("❌ Camera feed lost! Exiting...")
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    
    print(f"\nDetected {len(face_locations)} faces")  # Debug print

    # Process detected faces
    face_ids = []
    for face_location in face_locations:
        if not check_face_quality(face_location, frame):
            continue
            
        # Get face encoding for this specific face
        face_encoding = face_recognition.face_encodings(rgb_frame, [face_location])[0]
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
        name = "unknown"
        
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
        
        face_ids.append(name)
    
    # Check for presence of known and unknown faces
    known_present = any(face_id != "unknown" for face_id in face_ids)
    unknown_present = any(face_id == "unknown" for face_id in face_ids)
    
    # Handle case when both known and unknown faces are present
    if known_present and unknown_present and len(face_ids) >= 2:
        if "guest_with_known" not in sent_alerts:
            print("Known and unknown person detected together")
            snapshot_path = take_snapshot(frame, "guest_with_known")
            send_alert_in_background("No threat, it is probably your guest", snapshot_path)
            sent_alerts.add("guest_with_known")
        continue
    
    # Handle single known face
    if known_present and not unknown_present and len(face_ids) == 1:
        if "known_person" not in sent_alerts:
            print("Known person detected")
            snapshot_path = take_snapshot(frame, "known_person")
            send_alert_in_background("Welcome My Master!", snapshot_path)
            sent_alerts.add("known_person")
        continue
    
    # Handle unknown face
    if unknown_present:
        current_time = datetime.now()
        time_diff = (current_time - unknown_start_time).total_seconds()
        
        if time_diff > 5:  # Unknown person present for more than 5 seconds
            if current_time.hour >= 21 or current_time.hour < 6:  # Night time (9 PM to 6 AM)
                if "high_threat" not in sent_alerts:
                    print("High threat detected at night")
                    snapshot_path = take_snapshot(frame, "high_threat")
                    send_alert_in_background("Very high Threat detected", snapshot_path)
                    sent_alerts.add("high_threat")
            else:  # Day time
                if "normal_threat" not in sent_alerts:
                    print("Normal threat detected during day")
                    snapshot_path = take_snapshot(frame, "normal_threat")
                    send_alert_in_background("Normal threat", snapshot_path)
                    sent_alerts.add("normal_threat")
        else:
            unknown_start_time = current_time

    # Check for motion when no faces are detected
    if not face_locations:
        motion_detected, prev_frame = detect_motion(frame, prev_frame)
        if motion_detected and "motion_detected" not in sent_alerts:
            print("Motion detected but no face visible")
            snapshot_path = take_snapshot(frame, "motion")
            send_alert_in_background("⚠️ Motion detected but no face visible. Possible threat!", snapshot_path)
            sent_alerts.add("motion_detected")

    cv2.imshow("Surveillance Camera", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    time.sleep(0.1)

cap.release()
cv2.destroyAllWindows() 