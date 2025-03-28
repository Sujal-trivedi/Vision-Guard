import face_recognition
import cv2
import numpy as np
import os
import pickle
from tqdm import tqdm
import time

# Define directories
KNOWN_FACES_DIR = "dataset/known_faces"
AUGMENTED_FACES_DIR = "augmented_faces"
MODELS_DIR = "models"

# Create models directory if it doesn't exist
os.makedirs(MODELS_DIR, exist_ok=True)

def process_single_image(image_path, label_prefix=""):
    """Process a single image and extract face encodings"""
    try:
        # Load image
        image = cv2.imread(image_path)
        
        if image is None:
            print(f"⚠️ Could not load image: {os.path.basename(image_path)}")
            return None, None
            
        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Find face locations with a smaller upsample factor
        face_locations = face_recognition.face_locations(image, model="hog", number_of_times_to_upsample=1)
        
        if not face_locations:
            print(f"⚠️ No face found in: {os.path.basename(image_path)}")
            return None, None
        
        # Get face encodings
        encodings = face_recognition.face_encodings(image, face_locations)
        
        # Get label from filename (remove extension)
        label = os.path.splitext(os.path.basename(image_path))[0]
        if label_prefix:
            label = label_prefix + label
        
        return encodings, label
                
    except Exception as e:
        print(f"⚠️ Error processing {os.path.basename(image_path)}: {str(e)}")
        return None, None

def process_images(directory, label_prefix=""):
    """Process images in the given directory and extract face encodings"""
    print(f"\nProcessing images in {directory}...")
    
    # Initialize lists to store encodings and names
    all_encodings = []
    all_names = []
    
    # Get list of image files
    image_files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    # Process each image with progress bar
    for image_file in tqdm(image_files, desc="Processing images"):
        image_path = os.path.join(directory, image_file)
        
        # Process single image and wait for completion
        encodings, label = process_single_image(image_path, label_prefix)
        
        if encodings and label:
            # Add each encoding with the same label
            for encoding in encodings:
                all_encodings.append(encoding)
                all_names.append(label)
        
        # Add a small delay between processing images
        time.sleep(0.1)
    
    return all_encodings, all_names

def main():
    print("🔄 Starting face encoding process...")
    
    # Process known faces
    print("\nProcessing known faces...")
    known_encodings, known_names = process_images(KNOWN_FACES_DIR)
    
    # Process augmented faces
    print("\nProcessing augmented faces...")
    aug_encodings, aug_names = process_images(AUGMENTED_FACES_DIR, label_prefix="AUG_")
    
    # Combine all encodings and names
    all_encodings = known_encodings + aug_encodings
    all_names = known_names + aug_names
    
    if not all_encodings:
        print("❌ No face encodings were found!")
        return
    
    # Save encodings and names
    data = {
        "encodings": all_encodings,
        "names": all_names
    }
    
    output_path = os.path.join(MODELS_DIR, "face_encodings.pkl")
    with open(output_path, "wb") as f:
        pickle.dump(data, f)
    
    print(f"\n✅ Successfully processed {len(all_encodings)} faces")
    print(f"📁 Saved encodings to: {output_path}")
    print(f"👤 Unique labels: {set(all_names)}")

if __name__ == "__main__":
    main()
