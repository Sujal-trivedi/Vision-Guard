import cv2
import os
import time
from database import save_snapshot
from alert import send_whatsapp_alert

SNAPSHOT_DIR = "snapshots"

# Ensure directory exists
if not os.path.exists(SNAPSHOT_DIR):
    os.makedirs(SNAPSHOT_DIR)

def capture_and_send_snapshot(frame):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(SNAPSHOT_DIR, f"snapshot_{timestamp}.jpg")
    cv2.imwrite(filepath, frame)  # Save snapshot
    save_snapshot(filepath)  # Store in database

    send_whatsapp_alert(f"🚨 High-threat detected! Snapshot saved at {filepath}")
    print(f"[SNAPSHOT SAVED] {filepath}")
