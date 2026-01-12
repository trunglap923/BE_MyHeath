import firebase_admin
from firebase_admin import credentials, messaging
import logging
import os

logger = logging.getLogger(__name__)

# Hardcoded admin token from logic.py
ADMIN_TOKEN = "eUTg2c9UR5uoWyy6GgZt-P:APA91bHr1pCZmvtSm1Nahw6tHPm-2LA5foMGCuu-heYUrx8Dl4PpEE4GtmV60pN0GtHtbLCLcOr13Vpa5dVU9sPOEdI0zIUIU45k8nSniFTFoIFQNAc5QPc"

try:
    # Attempt to initialize Firebase
    # Check if app is already initialized to avoid error
    if not firebase_admin._apps:
        cred_path = "C:/Users/Admin/Desktop/MyHealth/foodai.json"
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized successfully.")
        else:
            logger.warning(f"Firebase credential file not found at {cred_path}. Notifications may not work.")
except Exception as e:
    logger.error(f"Failed to initialize Firebase: {e}")

def get_messaging():
    return messaging
