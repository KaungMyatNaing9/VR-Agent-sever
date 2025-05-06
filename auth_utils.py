import os
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import logging
from typing import Tuple, Optional
import pathlib

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Allow OAuth2 for HTTP (for local development only)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Create a credentials directory if it doesn't exist
CREDS_DIR = pathlib.Path("credentials")
CREDS_DIR.mkdir(exist_ok=True)

def create_oauth_flow(scopes: list = None) -> Flow:
    """
    Create a new OAuth2 flow instance for Google Calendar.
    
    Args:
        scopes: List of API scopes to request
        
    Returns:
        Google OAuth Flow object
    """
    if scopes is None:
        scopes = ['https://www.googleapis.com/auth/calendar']
        
    client_secrets_file = os.getenv('GOOGLE_CLIENT_SECRETS')
    redirect_uri = os.getenv('GOOGLE_OAUTH_REDIRECT_URI')
    
    logger.debug(f"Client secrets file: {client_secrets_file}")
    logger.debug(f"Redirect URI: {redirect_uri}")
    
    if not client_secrets_file or not redirect_uri:
        logger.error("Missing required environment variables for OAuth flow")
        raise ValueError("GOOGLE_CLIENT_SECRETS and GOOGLE_OAUTH_REDIRECT_URI must be set")
    
    try:
        flow = Flow.from_client_secrets_file(
            client_secrets_file,
            scopes=scopes,
            redirect_uri=redirect_uri
        )
        logger.debug("Successfully created OAuth flow")
        return flow
    except Exception as e:
        logger.error(f"Error creating OAuth flow: {str(e)}")
        raise

def get_authorization_url(flow: Flow) -> Tuple[str, str]:
    """
    Generate an authorization URL and state for the OAuth flow.
    
    Args:
        flow: Google OAuth Flow object
        
    Returns:
        Tuple of (auth_url, state)
    """
    try:
        auth_url, state = flow.authorization_url(
            access_type='offline',  # Enable refresh tokens
            include_granted_scopes='true',
            prompt='consent'
        )
        logger.debug(f"Generated auth URL: {auth_url}")
        logger.debug(f"Generated state: {state}")
        return auth_url, state
    except Exception as e:
        logger.error(f"Error generating authorization URL: {str(e)}")
        raise

def exchange_code_for_token(flow: Flow, authorization_response: str) -> Credentials:
    """
    Exchange an authorization code for access and refresh tokens.
    
    Args:
        flow: Google OAuth Flow object
        authorization_response: The full callback URL with auth code
        
    Returns:
        Google OAuth Credentials object
    """
    try:
        logger.debug(f"Exchanging code for token with response: {authorization_response}")
        flow.fetch_token(authorization_response=authorization_response)
        logger.debug("Successfully exchanged code for token")
        return flow.credentials
    except Exception as e:
        logger.error(f"Error exchanging code for token: {str(e)}")
        raise

def load_user_creds(user_id: str) -> Optional[str]:
    """
    Load a user's Google OAuth credentials from storage.
    In this implementation, we store credentials in files.
    
    Args:
        user_id: User identifier
        
    Returns:
        Credentials as JSON string or None if not found
    """
    creds_file = CREDS_DIR / f"{user_id}.json"
    logger.debug(f"Loading credentials from: {creds_file}")
    
    if not creds_file.exists():
        logger.info(f"No credentials found for user {user_id}")
        return None
    
    try:
        with open(creds_file, "r") as f:
            creds_json = f.read()
            
        # Try to refresh token if needed
        creds = Credentials.from_authorized_user_info(json.loads(creds_json))
        
        if creds.expired and creds.refresh_token:
            logger.debug("Token expired, attempting to refresh")
            creds.refresh(Request())
            # Update the stored credentials
            store_user_creds(user_id, creds.to_json())
            return creds.to_json()
            
        return creds_json
    except Exception as e:
        logger.error(f"Error loading credentials for user {user_id}: {str(e)}")
        return None

def store_user_creds(user_id: str, creds_json: str) -> bool:
    """
    Store a user's Google OAuth credentials.
    In this implementation, we store credentials in files.
    
    Args:
        user_id: User identifier
        creds_json: Credentials as JSON string
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Sanitize user_id to prevent directory traversal attacks
        user_id = user_id.replace('/', '_').replace('\\', '_')
        
        creds_file = CREDS_DIR / f"{user_id}.json"
        logger.debug(f"Storing credentials to: {creds_file}")
        
        with open(creds_file, "w") as f:
            f.write(creds_json)
        
        logger.info(f"Credentials for user {user_id} saved successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to store credentials for user {user_id}: {str(e)}")
        return False 