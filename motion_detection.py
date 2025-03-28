import cv2
import numpy as np

def detect_motion(frame, prev_frame=None):
    """Detect motion in the frame"""
    if prev_frame is None:
        prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return False, prev_frame
    
    # Convert current frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    prev_frame = cv2.GaussianBlur(prev_frame, (21, 21), 0)
    
    # Calculate frame difference
    frame_diff = cv2.absdiff(gray, prev_frame)
    
    # Apply threshold to get binary image (increased threshold)
    thresh = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)[1]
    
    # Dilate the thresholded image to fill in holes
    thresh = cv2.dilate(thresh, None, iterations=2)
    
    # Find contours on thresholded image
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Calculate total motion area
    total_motion_area = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 100:  # Minimum area threshold increased
            total_motion_area += area
    
    # Calculate motion percentage
    frame_area = frame.shape[0] * frame.shape[1]
    motion_percentage = total_motion_area / frame_area
    
    # Only return True if motion is significant (more than 0.1% of frame)
    if motion_percentage > 0.001:
        # Update previous frame only if significant motion is detected
        prev_frame = gray.copy()
        return True, prev_frame
    
    # Update previous frame
    prev_frame = gray.copy()
    return False, prev_frame 