# Vision-Guard
Its your very own Survaillance System

files that you will have to create
1) augment_faces.py
   
2) owner_labels.py
   
3) env for twilio

4) config.py
   
what is our model
The system uses a Streamlit-based dashboard interface that provides real-time monitoring and control of the surveillance system.

It integrates with Cloudinary for cloud storage of surveillance snapshots, allowing secure and efficient image management.

The dashboard features two main sections: a Home page with project information and a Surveillance Dashboard for real-time monitoring.

The Surveillance Dashboard displays key statistics including total snapshots, alerts, recent alerts, and system uptime through visually appealing gradient cards.

The system maintains a live camera feed that automatically updates to show the most recent surveillance footage.

Alerts are managed through a JSON file system, where the system tracks and displays recent alerts with timestamps and messages.

The dashboard includes a snapshot gallery that shows recent surveillance images in a grid layout, with options to view details and delete images.

The interface uses modern UI elements like status indicators, gradient cards, and hover effects to provide a professional user experience.

The system automatically calculates time differences for snapshots and alerts, showing how recent each item is (e.g., "Just now", "5 minutes ago").

All data is presented in a responsive layout that works across different screen sizes, with real-time updates and manual refresh options available to the user.

