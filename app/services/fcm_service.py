import os
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

_firebase_initialized = False

def init_firebase_admin():
    global _firebase_initialized
    if _firebase_initialized:
        return
        
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
    if os.path.exists(cred_path):
        try:
            import firebase_admin
            from firebase_admin import credentials
            if not firebase_admin._apps:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized successfully!")
                _firebase_initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
    else:
        logger.info(f"Firebase credentials file not found at '{cred_path}'. Running in development mode.")

# Try initializing on module load
init_firebase_admin()

def send_fcm_notification(device_token: str, title: str, body: str, data_payload: Optional[Dict[str, str]] = None) -> bool:
    """
    Sends real FCM push notification to a target device token via @react-native-firebase/messaging.
    """
    try:
        import firebase_admin
        from firebase_admin import messaging
        
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data_payload or {},
            token=device_token
        )
        response = messaging.send(message)
        logger.info(f"FCM Notification sent successfully to token {device_token[:10]}... Message ID: {response}")
        return True
    except Exception as e:
        logger.warning(f"FCM Messaging fallback mode (No live token / Firebase credentials missing): {e}")
        return False
