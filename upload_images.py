import time
import os
import cloudinary.uploader
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import config
from datetime import datetime

FOLDER_TO_WATCH = r"C:\Users\Acer\OneDrive\Desktop\VISION GUARD\snapshots"

class SnapshotHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(f"[{datetime.now()}] New image detected: {event.src_path}")
            try:
                # Add a small delay to ensure file is completely written
                time.sleep(0.5)
                image_url = upload_to_cloudinary(event.src_path)
                if image_url:
                    print(f"[{datetime.now()}] Successfully uploaded: {image_url}")
            except Exception as e:
                print(f"[{datetime.now()}] Error uploading image: {str(e)}")

def upload_to_cloudinary(image_path):
    try:
        # Verify file exists and is readable
        if not os.path.exists(image_path):
            print(f"Error: File does not exist: {image_path}")
            return None
            
        print(f"Attempting to upload file: {image_path}")
        print(f"File size: {os.path.getsize(image_path)} bytes")
        
        # Add unique public_id based on timestamp
        timestamp = int(time.time())
        response = cloudinary.uploader.upload(
            image_path,
            public_id=f"surveillance_{timestamp}",
            overwrite=True
        )
        print(f"Upload response: {response}")  # Debug print
        return response['secure_url']
    except Exception as e:
        print(f"Upload error: {str(e)}")
        print(f"Error type: {type(e)}")  # Print error type
        return None

if __name__ == "__main__":
    print(f"[{datetime.now()}] Starting surveillance monitoring...")
    print(f"Watching folder: {FOLDER_TO_WATCH}")
    
    # Verify folder exists
    if not os.path.exists(FOLDER_TO_WATCH):
        os.makedirs(FOLDER_TO_WATCH)
        print(f"Created monitoring folder: {FOLDER_TO_WATCH}")

    event_handler = SnapshotHandler()
    observer = Observer()
    observer.schedule(event_handler, FOLDER_TO_WATCH, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping surveillance monitoring...")
        observer.stop()
    observer.join()
