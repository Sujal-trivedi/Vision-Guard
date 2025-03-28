import cv2
import face_recognition
import numpy as np
import pickle
import os

def load_known_faces():
    """Load known face encodings from file"""
    ENCODINGS_FILE = "models/face_encodings.pkl"
    known_face_encodings, known_face_names = [], []
    
    if os.path.exists(ENCODINGS_FILE):
        with open(ENCODINGS_FILE, "rb") as f:
            data = pickle.load(f)
            known_face_encodings = data.get("encodings", [])
            known_face_names = data.get("names", [])
    else:
        print("⚠️ Warning: No known faces found!")
    
    return known_face_encodings, known_face_names

def get_lighting_thresholds(brightness):
    """Get thresholds based on lighting conditions"""
    if brightness < 30:  # Very dim
        return {
            'edge_density': 0.015,
            'vertical_density': 0.003,
            'color_std': 10,
            'motion_density': 0.0001,
            'tolerance': 0.65
        }
    elif brightness < 60:  # Dim
        return {
            'edge_density': 0.02,
            'vertical_density': 0.005,
            'color_std': 15,
            'motion_density': 0.0002,
            'tolerance': 0.6
        }
    elif brightness < 120:  # Normal
        return {
            'edge_density': 0.025,
            'vertical_density': 0.008,
            'color_std': 20,
            'motion_density': 0.0003,
            'tolerance': 0.55
        }
    else:  # Bright
        return {
            'edge_density': 0.03,
            'vertical_density': 0.01,
            'color_std': 25,
            'motion_density': 0.0005,
            'tolerance': 0.5
        }

def check_face_quality(face_location, frame):
    """Check if the detected face meets quality criteria"""
    try:
        # Get face coordinates and dimensions
        top, right, bottom, left = face_location
        face_width = right - left
        face_height = bottom - top
        face_area = face_width * face_height
        frame_area = frame.shape[0] * frame.shape[1]
        face_ratio = face_area / frame_area
        
        # Check face size
        if face_ratio < 0.0005 or face_ratio > 0.4:
            print(f"Face size check failed: {face_ratio:.4f}")
            return False
            
        # Extract and validate face region
        face_region = frame[top:bottom, left:right]
        if face_region.size == 0:
            print("Invalid face region")
            return False
            
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(face_region, cv2.COLOR_RGB2GRAY)
        brightness = np.mean(gray)
        thresholds = get_lighting_thresholds(brightness)
        
        # Calculate edge and vertical densities
        edges = cv2.Canny(gray, 30, 100)
        edge_density = np.sum(edges > 0) / edges.size
        
        vertical_edges = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        vertical_density = np.sum(np.abs(vertical_edges) > 20) / vertical_edges.size
        
        # Calculate color variation
        color_std = np.std(face_region)
        
        # Check all criteria
        if (edge_density < thresholds['edge_density'] or
            vertical_density < thresholds['vertical_density'] or
            color_std < thresholds['color_std']):
            print(f"Face quality check failed: edge={edge_density:.4f}, vertical={vertical_density:.4f}, color={color_std:.2f}")
            return False
            
        return True
        
    except Exception as e:
        print(f"Error in face quality check: {str(e)}")
        return False

def is_human_shape(face_location, frame):
    """Check if the detected shape is human-like"""
    try:
        # Get face coordinates and expand region
        top, right, bottom, left = face_location
        height, width = frame.shape[:2]
        body_top = max(0, top - int((bottom - top) * 1.5))
        body_bottom = min(height, bottom + int((bottom - top) * 1.0))
        body_left = max(0, left - int((right - left) * 1.0))
        body_right = min(width, right + int((right - left) * 1.0))
        
        # Extract and validate body region
        body_region = frame[body_top:body_bottom, body_left:body_right]
        if body_region.size == 0:
            return False
            
        # Convert to grayscale and analyze
        gray = cv2.cvtColor(body_region, cv2.COLOR_RGB2GRAY)
        brightness = np.mean(gray)
        thresholds = get_lighting_thresholds(brightness)
        
        # Calculate edge and vertical densities
        edges = cv2.Canny(gray, 10, 50)
        edge_density = np.sum(edges > 0) / edges.size
        
        vertical_edges = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        vertical_density = np.sum(np.abs(vertical_edges) > 10) / vertical_edges.size
        
        # Calculate motion density if previous frame exists
        motion_density = 0
        if hasattr(is_human_shape, 'prev_frame'):
            if gray.shape == is_human_shape.prev_frame.shape:
                motion = cv2.absdiff(gray, is_human_shape.prev_frame)
                motion_density = np.sum(motion > 5) / motion.size
        
        # Update previous frame
        is_human_shape.prev_frame = gray.copy()
        
        # Check if it's a human shape
        is_human = (edge_density >= thresholds['edge_density'] and 
                   vertical_density >= thresholds['vertical_density'] and 
                   (motion_density >= thresholds['motion_density'] or motion_density == 0))
        
        if not is_human:
            print(f"Human shape check failed: edge={edge_density:.4f}, vertical={vertical_density:.4f}, motion={motion_density:.4f}")
            return False
            
        return True
        
    except Exception as e:
        print(f"Error in human shape check: {str(e)}")
        return False

def get_face_recognition_tolerance(face_location, frame):
    """Get optimal face recognition tolerance based on conditions"""
    try:
        # Get face coordinates and dimensions
        top, right, bottom, left = face_location
        face_width = right - left
        face_height = bottom - top
        aspect_ratio = face_width / face_height
        
        # Extract face region and analyze
        face_region = frame[top:bottom, left:right]
        gray = cv2.cvtColor(face_region, cv2.COLOR_RGB2GRAY)
        brightness = np.mean(gray)
        thresholds = get_lighting_thresholds(brightness)
        
        # Calculate face size ratio
        face_area = face_width * face_height
        frame_area = frame.shape[0] * frame.shape[1]
        face_ratio = face_area / frame_area
        
        # Adjust tolerance based on conditions
        tolerance = thresholds['tolerance']
        
        # Adjust for face angle
        if aspect_ratio < 0.7 or aspect_ratio > 1.3:  # Side face
            tolerance += 0.1
        elif aspect_ratio < 0.8 or aspect_ratio > 1.2:  # Slightly angled
            tolerance += 0.05
            
        # Adjust for face size
        if face_ratio < 0.005 or face_ratio > 0.2:
            tolerance += 0.05
            
        return min(tolerance, 0.75)  # Cap maximum tolerance
        
    except Exception as e:
        print(f"Error calculating tolerance: {str(e)}")
        return 0.6  # Default tolerance 