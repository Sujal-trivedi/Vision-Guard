import json
import os
import threading
from datetime import datetime
import cv2
from alert import send_whatsapp_alert

# Constants
SNAPSHOT_DIR = "snapshots"
ALERTS_FILE = "alerts.json"

def take_snapshot(frame, label):
    """Take a snapshot of the current frame"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    snapshot_path = f"{SNAPSHOT_DIR}/{label}_{timestamp}.jpg"
    cv2.imwrite(snapshot_path, frame)
    return snapshot_path

def send_alert_in_background(message, snapshot_path=None):
    """Send alert in background thread"""
    def send():
        try:
            # Print alert to terminal
            print(f"\n🔔 Alert: {message}")
            if snapshot_path:
                print(f"📸 Snapshot saved: {snapshot_path}")
            
            # Send WhatsApp alert
            send_whatsapp_alert(message, snapshot_path)
            
            # Update alerts file
            alerts = []
            if os.path.exists(ALERTS_FILE):
                try:
                    with open(ALERTS_FILE, "r") as f:
                        content = f.read()
                        if content.strip():  # Check if file is not empty
                            alerts = json.loads(content)
                except json.JSONDecodeError:
                    # If file is corrupted or empty, start with empty list
                    alerts = []
            
            alerts.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "message": message,
                "snapshot": snapshot_path
            })
            
            with open(ALERTS_FILE, "w") as f:
                json.dump(alerts, f, indent=4)
                
        except Exception as e:
            print(f"Error sending alert: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    # Start alert thread
    alert_thread = threading.Thread(target=send)
    alert_thread.daemon = True
    alert_thread.start() 