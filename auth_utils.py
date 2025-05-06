import os
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

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
    
    if not client_secrets_file or not redirect_uri:
        logger.error("Missing required environment variables for OAuth flow")
        raise ValueError("GOOGLE_CLIENT_SECRETS and GOOGLE_OAUTH_REDIRECT_URI must be set")
    
    flow = Flow.from_client_secrets_file(
        client_secrets_file,
        scopes=scopes,
        redirect_uri=redirect_uri
    )
    
    return flow

def get_authorization_url(flow: Flow) -> Tuple[str, str]:
    """
    Generate an authorization URL and state for the OAuth flow.
    
    Args:
        flow: Google OAuth Flow object
        
    Returns:
        Tuple of (auth_url, state)
    """
    auth_url, state = flow.authorization_url(
        access_type='offline',  # Enable refresh tokens
        include_granted_scopes='true',
        prompt='consent'
    )
    
    return auth_url, state

def exchange_code_for_token(flow: Flow, authorization_response: str) -> Credentials:
    """
    Exchange an authorization code for access and refresh tokens.
    
    Args:
        flow: Google OAuth Flow object
        authorization_response: The full callback URL with auth code
        
    Returns:
        Google OAuth Credentials object
    """
    flow.fetch_token(authorization_response=authorization_response)
    return flow.credentials

def load_user_creds(user_id: str) -> Optional[str]:
    """
    Load a user's Google OAuth credentials from storage.
    In a production system, this would load from a secure database.
    
    Args:
        user_id: User identifier
        
    Returns:
        Credentials as JSON string or None if not found
    """
    # This is a placeholder. In a real system, you would:
    # 1. Look up the user in your database
    # 2. Retrieve their stored credentials
    # 3. Check if the credentials are expired and refresh if needed
    
    # For demo purposes, we're returning None to indicate no credentials found
    return None

def store_user_creds(user_id: str, creds_json: str) -> bool:
    """
    Store a user's Google OAuth credentials.
    In a production system, this would save to a secure database.
    
    Args:
        user_id: User identifier
        creds_json: Credentials as JSON string
        
    Returns:
        True if successful, False otherwise
    """
    # This is a placeholder. In a real system, you would:
    # 1. Look up the user in your database
    # 2. Store their credentials securely
    # 3. Set appropriate expiration or refresh mechanics
    
    try:
        # Simulate successful storage
        return True
    except Exception as e:
        logger.error(f"Failed to store credentials for user {user_id}: {e}")
        return False 