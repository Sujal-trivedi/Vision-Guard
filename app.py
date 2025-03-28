git hub vision guard app.py


import streamlit as st
import cloudinary.api
import config
import time
from datetime import datetime
import pytz
from PIL import Image
import requests
from io import BytesIO
import os
import json

# Constants
STANDARD_WIDTH = 400
STANDARD_HEIGHT = 300

# Page Configuration
st.set_page_config(
    page_title="CCTV Surveillance System",
    page_icon="📹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #2c3e50, #3498db);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stat-card {
        background: linear-gradient(135deg, #3498db, #2980b9);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .alert-card {
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .camera-feed {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .status-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
    }
    .status-active {
        background-color: #2ecc71;
        box-shadow: 0 0 10px #2ecc71;
    }
    .status-inactive {
        background-color: #e74c3c;
        box-shadow: 0 0 10px #e74c3c;
    }
    .snapshot-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 15px;
        padding: 15px;
    }
    .snapshot-item {
        position: relative;
        border-radius: 8px;
        overflow: hidden;
        cursor: pointer;
        transition: transform 0.3s ease;
    }
    .snapshot-item:hover {
        transform: scale(1.05);
    }
    .snapshot-info {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(0,0,0,0.7);
        color: white;
        padding: 8px;
        font-size: 0.8rem;
    }
    </style>
    """, unsafe_allow_html=True)

def get_system_stats():
    """Get system statistics"""
    try:
        # Get number of snapshots
        snapshots = [f for f in os.listdir("snapshots") if f.endswith(('.jpg', '.jpeg', '.png'))]
        num_snapshots = len(snapshots)
        
        # Get latest alerts
        alerts = []
        if os.path.exists("alerts.json"):
            with open("alerts.json", "r") as f:
                alerts = json.load(f)
        
        # Calculate statistics
        total_alerts = len(alerts)
        recent_alerts = len([a for a in alerts if (datetime.now() - datetime.strptime(a["timestamp"], "%Y-%m-%d %H:%M:%S")).days < 1])
        threat_alerts = len([a for a in alerts if "threat" in a["message"].lower()])
        
        return {
            "num_snapshots": num_snapshots,
            "total_alerts": total_alerts,
            "recent_alerts": recent_alerts,
            "threat_alerts": threat_alerts,
            "system_uptime": get_system_uptime()
        }
    except Exception as e:
        st.error(f"Error getting system stats: {str(e)}")
        return {
            "num_snapshots": 0,
            "total_alerts": 0,
            "recent_alerts": 0,
            "threat_alerts": 0,
            "system_uptime": "0:00:00"
        }

def get_system_uptime():
    """Calculate system uptime"""
    try:
        if os.path.exists("alerts.json"):
            with open("alerts.json", "r") as f:
                alerts = json.load(f)
                if alerts:
                    first_alert = datetime.strptime(alerts[0]["timestamp"], "%Y-%m-%d %H:%M:%S")
                    uptime = datetime.now() - first_alert
                    hours = int(uptime.total_seconds() // 3600)
                    minutes = int((uptime.total_seconds() % 3600) // 60)
                    seconds = int(uptime.total_seconds() % 60)
                    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except:
        pass
    return "00:00:00"

def delete_image(public_id):
    try:
        result = cloudinary.uploader.destroy(public_id)
        if result.get('result') == 'ok':
            st.success("Image deleted successfully!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Failed to delete image")
    except Exception as e:
        st.error(f"Error deleting image: {str(e)}")

def time_difference(timestamp_str):
    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%SZ')
    timestamp = pytz.utc.localize(timestamp)
    now = datetime.now(pytz.utc)
    diff = now - timestamp
    minutes = int(diff.total_seconds() / 60)
    
    if minutes < 1:
        return "Just now"
    elif minutes == 1:
        return "1 minute ago"
    elif minutes < 60:
        return f"{minutes} minutes ago"
    elif minutes < 1440:
        hours = minutes // 60
        return f"{hours} hours ago"
    else:
        days = minutes // 1440
        return f"{days} days ago"

def fetch_latest_images():
    try:
        resources = cloudinary.api.resources(
            type="upload",
            prefix="surveillance_",
            max_results=12,
            sort_by="created_at",
            direction="desc"
        )
        
        sorted_resources = sorted(
            resources['resources'],
            key=lambda x: datetime.strptime(x['created_at'], '%Y-%m-%dT%H:%M:%SZ'),
            reverse=True
        )
        
        return [(
            res['secure_url'],
            res['created_at'],
            datetime.strptime(res['created_at'], '%Y-%m-%dT%H:%M:%SZ'),
            res['public_id']
        ) for res in sorted_resources]
    except Exception as e:
        st.error(f"Error fetching images: {str(e)}")
        return []

def get_resized_image(image_url):
    try:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        img.thumbnail((STANDARD_WIDTH, STANDARD_HEIGHT), Image.Resampling.LANCZOS)
        new_img = Image.new("RGB", (STANDARD_WIDTH, STANDARD_HEIGHT), "white")
        paste_x = (STANDARD_WIDTH - img.width) // 2
        paste_y = (STANDARD_HEIGHT - img.height) // 2
        new_img.paste(img, (paste_x, paste_y))
        return new_img
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

# Navigation
page = st.sidebar.radio("Navigation", ["Home", "Surveillance Dashboard"])

if page == "Home":
    # Landing Page Content
    st.markdown('<div class="main-header"><h1>Smart CCTV Surveillance System</h1></div>', unsafe_allow_html=True)

    # Project Overview
    st.header("🎯 Project Overview")
    st.write("""
    This intelligent CCTV surveillance system leverages deep learning to enhance security through automated face detection 
    and unknown person identification. The system operates continuously, providing real-time monitoring and instant alerts 
    for enhanced security measures.
    """)

    # Key Features
    st.header("🔑 Key Features")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        - **24/7 Surveillance** with enhanced monitoring
        - **Real-time Face Detection** using deep learning
        - **Unknown Person Detection** with instant alerts
        - **Cloud Storage** integration with Cloudinary
        """)
    with col2:
        st.markdown("""
        - **WhatsApp Alerts** for immediate notification
        - **Special Night Mode** (9 PM - 9 AM)
        - **Web Interface** for easy monitoring
        - **Secure Image Management**
        """)

    # Technology Stack
    st.header("💻 Technology Stack")
    tech_col1, tech_col2, tech_col3 = st.columns(3)
    
    with tech_col1:
        st.subheader("Frontend")
        st.markdown("""
        - Streamlit
        - HTML/CSS
        - Python
        """)
    
    with tech_col2:
        st.subheader("Backend")
        st.markdown("""
        - Python
        - OpenCV
        - Deep Learning Models
        """)
    
    with tech_col3:
        st.subheader("Cloud & Services")
        st.markdown("""
        - Cloudinary
        - WhatsApp API
        - Face Recognition
        """)

    # Team Members (Simplified)
    st.header("👥 Team Members")
    st.markdown("""
    - Sujal Trivedi
    - Akash Purohit
    - Arya Wankhade
    - Vinayak Sahu
    """)

else:  # Surveillance Dashboard
    # System Status and Controls
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📷 Surveillance Dashboard")
    with col2:
        st.markdown("""
            <div style='text-align: right; margin-top: 20px;'>
                <span class='status-indicator status-active'></span>
                <span style='color: #2ecc71;'>Active</span>
            </div>
        """, unsafe_allow_html=True)

    # Stats Row
    stats = get_system_stats()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class='stat-card'>
                <h3>Total Snapshots</h3>
                <h2>{stats['num_snapshots']}</h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class='stat-card'>
                <h3>Total Alerts</h3>
                <h2>{stats['total_alerts']}</h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class='stat-card'>
                <h3>Recent Alerts</h3>
                <h2>{stats['recent_alerts']}</h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class='stat-card'>
                <h3>System Uptime</h3>
                <h2>{stats['system_uptime']}</h2>
            </div>
        """, unsafe_allow_html=True)

    # Controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button('🔄 Refresh Dashboard', use_container_width=True):
            st.rerun()
    with col2:
        if st.button('🗑️ Clear Alerts', use_container_width=True):
            if os.path.exists("alerts.json"):
                os.remove("alerts.json")
            st.success("Alerts cleared successfully!")
            st.rerun()

    # Camera Feed and Alerts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📹 Live Camera Feed")
        latest_images = fetch_latest_images()
        if latest_images:
            latest_img = get_resized_image(latest_images[0][0])
            if latest_img:
                st.image(latest_img, use_container_width=True)
                st.markdown(f"**Last Updated:** {time_difference(latest_images[0][1])}")
        else:
            st.info("No camera feed available")

    with col2:
        st.markdown("### ⚠️ Recent Alerts")
        if os.path.exists("alerts.json"):
            with open("alerts.json", "r") as f:
                alerts = json.load(f)
                for alert in alerts[-5:]:  # Show last 5 alerts
                    st.markdown(f"""
                        <div class='alert-card'>
                            <strong>{alert['timestamp']}</strong><br>
                            {alert['message']}
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No alerts available")

    # Snapshots Grid
    st.markdown("### 📸 Recent Snapshots")
    images = fetch_latest_images()
    
    if images:
        cols = st.columns(3)
        for i, (img_url, created_at, timestamp, public_id) in enumerate(images):
            with cols[i % 3]:
                with st.container():
                    resized_img = get_resized_image(img_url)
                    if resized_img:
                        st.image(resized_img, use_container_width=True)
                    
                    local_time = timestamp.replace(tzinfo=pytz.UTC).astimezone()
                    
                    st.markdown(f"""
                        <div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px;'>
                            <strong>Date:</strong> {local_time.strftime('%B %d, %Y')}<br>
                            <strong>Time:</strong> {local_time.strftime('%I:%M:%S %p')}<br>
                            <strong>Status:</strong> {time_difference(created_at)}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("🗑️ Delete", key=f"delete_{public_id}", use_container_width=True):
                        delete_image(public_id)
                    
                    st.markdown("---")
    else:
        st.info("No snapshots available")

    st.text(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
