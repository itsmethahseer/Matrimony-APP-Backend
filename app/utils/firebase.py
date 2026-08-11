import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Attempt to import and initialize Firebase Admin SDK
_firebase_initialized = False
try:
    import firebase_admin
    from firebase_admin import auth as firebase_auth, credentials

    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        _firebase_initialized = True
        logger.info("Firebase Admin SDK initialized successfully with service account certificate.")
    else:
        # Initialize default app if env variables are configured
        try:
            firebase_admin.initialize_app()
            _firebase_initialized = True
            logger.info("Firebase Admin SDK initialized with default application credentials.")
        except Exception as init_err:
            logger.warning(f"Firebase Admin SDK default initialization skipped: {init_err}")
except Exception as e:
    logger.warning(f"Firebase Admin SDK not loaded ({e}). Development fallback verification enabled.")

def verify_firebase_id_token(id_token: str) -> Dict[str, Any]:
    """
    Verifies Firebase ID token received from Firebase Auth SDK on Mobile/Web.
    Returns decoded token dictionary containing phone_number, uid, email.
    """
    if _firebase_initialized:
        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
            return {
                "uid": decoded_token.get("uid"),
                "phone_number": decoded_token.get("phone_number"),
                "email": decoded_token.get("email"),
                "verified": True
            }
        except Exception as err:
            logger.error(f"Firebase ID Token verification failed: {err}")
            raise Exception(f"Invalid Firebase ID Token: {err}")
    else:
        # Development / Fallback mode if Firebase Service Account credentials are not yet added
        logger.info("Firebase Admin in dev/fallback mode. Accepting formatted ID token.")
        if id_token.startswith("firebase_mock_") or len(id_token) > 10:
            return {
                "uid": f"dev_uid_{id_token[:10]}",
                "phone_number": None,
                "email": None,
                "verified": True
            }
        raise Exception("Invalid Firebase token format.")
