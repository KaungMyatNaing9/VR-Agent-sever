import os
import json
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, Depends, HTTPException, Response, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
import openai
from dotenv import load_dotenv

# Local imports
from schemas import ChatRequest, ChatResponse, AuthResponse
from function_specs import FUNCTION_SPECS
import calendar_service
import auth_utils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Check for required environment variables
required_env_vars = ['OPENAI_API_KEY', 'GOOGLE_CLIENT_SECRETS', 'GOOGLE_OAUTH_REDIRECT_URI']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Create FastAPI app
app = FastAPI(
    title="VR Agent API",
    description="API for VR Agent with calendar integration",
    version="0.1.0"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify your allowed origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth flow storage (in-memory for demo, use Redis or similar in production)
oauth_states = {}  # Maps state to user_id

@app.get("/")
async def root():
    """Root endpoint to check if API is running"""
    return {"status": "online", "message": "VR Agent API is running"}

@app.get("/auth/google")
async def auth_google(user_id: str = Query(..., description="User identifier")):
    """
    Initiate Google OAuth flow
    
    Args:
        user_id: Identifier for the user starting authentication
    
    Returns:
        Redirect to Google's OAuth consent screen
    """
    try:
        # Create OAuth flow
        flow = auth_utils.create_oauth_flow()
        
        # Generate authorization URL and state
        auth_url, state = auth_utils.get_authorization_url(flow)
        
        # Store state with user_id for verification in callback
        oauth_states[state] = user_id
        
        # Redirect to Google's authorization page
        return RedirectResponse(auth_url)
    except Exception as e:
        logger.error(f"OAuth initiation error: {e}")
        return AuthResponse(
            status="error",
            message=f"Failed to initiate authentication: {str(e)}"
        )

@app.get("/auth/callback")
async def auth_callback(request: Request):
    """
    Handle OAuth callback from Google
    
    Args:
        request: FastAPI request object containing auth code and state
    
    Returns:
        Authentication status
    """
    try:
        # Get the full URL with query parameters
        authorization_response = str(request.url)
        
        # Extract state from query parameters
        query_params = dict(request.query_params)
        state = query_params.get("state")
        
        if not state or state not in oauth_states:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OAuth state"
            )
        
        # Get the user_id associated with this state
        user_id = oauth_states[state]
        
        # Remove the state from storage to prevent replay attacks
        del oauth_states[state]
        
        # Create a new flow with the same parameters as the original
        flow = auth_utils.create_oauth_flow()
        
        # Exchange auth code for tokens
        credentials = auth_utils.exchange_code_for_token(flow, authorization_response)
        
        # Store credentials for the user
        creds_json = credentials.to_json()
        auth_utils.store_user_creds(user_id, creds_json)
        
        return AuthResponse(
            status="success",
            message="Successfully authenticated with Google Calendar"
        )
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        return AuthResponse(
            status="error",
            message=f"Authentication failed: {str(e)}"
        )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint with function calling capability
    
    Args:
        request: Chat request containing user message and user ID
    
    Returns:
        Assistant's response
    """
    try:
        user_msg = request.message
        user_id = request.user_id
        
        # Load user credentials
        creds_json = auth_utils.load_user_creds(user_id)
        
        # Prepare system message based on authentication status
        system_content = "You are a helpful VR assistant."
        if creds_json:
            system_content += " You can access the user's Google Calendar."
        else:
            system_content += " The user has not connected their Google Calendar yet."
        
        # Create messages for the API call
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_msg}
        ]
        
        # Call OpenAI API with function definitions if user is authenticated
        if creds_json:
            completion = openai.chat.completions.create(
                model="gpt-4o-mini",  # or your preferred model
                messages=messages,
                tools=[{"type": "function", "function": func} for func in FUNCTION_SPECS],
                tool_choice="auto"
            )
        else:
            completion = openai.chat.completions.create(
                model="gpt-4o-mini",  # or your preferred model
                messages=messages
            )
        
        # Extract the response message
        response_message = completion.choices[0].message
        
        # Check if a function call was generated
        if hasattr(response_message, 'tool_calls') and response_message.tool_calls:
            tool_call = response_message.tool_calls[0]
            
            # Only process function calls if user is authenticated
            if not creds_json:
                return ChatResponse(
                    reply="To perform calendar operations, you need to connect your Google Calendar first. "
                          "Please authenticate to enable this feature."
                )
            
            # Extract function name and arguments
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Add credentials to function arguments
            function_args['creds_json'] = creds_json
            
            # Call the appropriate calendar service function
            if hasattr(calendar_service, function_name):
                function_to_call = getattr(calendar_service, function_name)
                function_result = function_to_call(**function_args)
                
                # Add the function response to messages
                messages.append(response_message.model_dump())
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name, 
                    "content": json.dumps(function_result)
                })
                
                # Get a follow-up response from the model
                second_completion = openai.chat.completions.create(
                    model="gpt-4o-mini",  # or your preferred model
                    messages=messages
                )
                
                # Return the follow-up response
                return ChatResponse(
                    reply=second_completion.choices[0].message.content
                )
            else:
                logger.error(f"Unknown function: {function_name}")
                return ChatResponse(
                    reply="I'm sorry, but I encountered an error trying to execute that operation."
                )
        
        # Return the model's response if no function call was made
        return ChatResponse(
            reply=response_message.content
        )
    
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"An error occurred: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 