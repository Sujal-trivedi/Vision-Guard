from twilio.rest import Client
import os
from dotenv import load_dotenv
import time
import requests
from urllib.parse import quote

# Load environment variables
load_dotenv()

# Your Twilio Account SID and Auth Token
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

def send_whatsapp_alert(message, snapshot_path=None):
    try:
        # Your Twilio WhatsApp number (with country code)
        from_whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
        # The recipient's WhatsApp number (with country code)
        to_whatsapp_number = os.getenv('RECIPIENT_WHATSAPP_NUMBER')
        
        if not from_whatsapp_number or not to_whatsapp_number:
            print("❌ Error: WhatsApp numbers not configured in .env file")
            return
            
        # Format WhatsApp numbers
        from_whatsapp_number = f"whatsapp:{from_whatsapp_number}"
        to_whatsapp_number = f"whatsapp:{to_whatsapp_number}"
        
        # Prepare the message
        if snapshot_path and os.path.exists(snapshot_path):
            # If there's a snapshot, send it with the message
            # First, upload the image to a publicly accessible URL
            # For now, we'll just send the message without the image
            # TODO: Implement proper image upload and URL generation
            message = client.messages.create(
                from_=from_whatsapp_number,
                body=message,
                to=to_whatsapp_number
            )
        else:
            # If no snapshot, just send the message
            message = client.messages.create(
                from_=from_whatsapp_number,
                body=message,
                to=to_whatsapp_number
            )
            
        print(f"✅ WhatsApp alert sent successfully: {message.sid}")
        
    except Exception as e:
        error_msg = str(e)
        if "exceeded the null daily messages limit" in error_msg:
            print("⚠️ Twilio daily message limit reached. Please try again later.")
        elif "HTTP Error" in error_msg:
            print("❌ Twilio API Error: Please check your account credentials and permissions")
            print(f"Error details: {error_msg}")
        else:
            print(f"❌ Error sending WhatsApp alert: {error_msg}")
            # Print more detailed error information
            import traceback
            print(traceback.format_exc())
        
        # Add a delay before retrying to avoid rate limiting
        time.sleep(5)
