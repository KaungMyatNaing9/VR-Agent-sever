# VR-Agent-Server

A FastAPI backend server for LLM endpoints with Google Calendar integration for VR applications.

## Overview

This server provides a chat interface that can:

1. Answer general user questions using OpenAI's GPT models
2. Perform calendar operations via Google Calendar API
3. Handle OAuth authentication with Google

## Architecture

```
[User] --> POST /chat --> [FastAPI Handler]
                          |--> [OpenAI GPT] --(function_call)--> [Dispatcher]
                                                             |--> [Calendar Service] --> Google Calendar
                          |<-- (reply) -----------------------|
```

## Prerequisites

1. **OpenAI API Key**: Sign up at [OpenAI](https://platform.openai.com/) and obtain an API key
2. **Google Cloud Setup**:
   - Create a project in [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Google Calendar API
   - Create OAuth2 Web Application credentials
   - Download client_secret.json file
3. **Python 3.8+**: Required for running the application

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/VR-Agent-server.git
   cd VR-Agent-server
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with the following variables:

   ```
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_CLIENT_SECRETS=path/to/client_secret.json
   GOOGLE_OAUTH_REDIRECT_URI=https://your-domain.com/auth/callback
   ```

   For local development, you can use:

   ```
   GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback
   ```

## Running the Server

Start the server with:

```
uvicorn app:app --reload
```

The server will be available at http://localhost:8000 by default.

## API Endpoints

### Authentication

- `GET /auth/google?user_id=123`: Initiates Google OAuth flow for the specified user
- `GET /auth/callback`: Handles OAuth callback from Google (automatically called after authorization)

### Chat

- `POST /chat`: Main chat endpoint with LLM and calendar capabilities

  Request body:

  ```json
  {
    "message": "What's on my calendar today?",
    "user_id": "123"
  }
  ```

  Response:

  ```json
  {
    "reply": "You have a meeting at 3pm with Alex about project planning."
  }
  ```

## Calendar Capabilities

The assistant can perform the following calendar operations:

1. **List Events**: View upcoming calendar events in a specified time window
2. **Create Events**: Add new events to the calendar
3. **Update Events**: Modify existing events
4. **Delete Events**: Remove events from the calendar

## Setting Up Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Create OAuth credentials (Web application type)
5. Add your redirect URI (e.g., http://localhost:8000/auth/callback for local development)
6. Download the client_secret.json file
7. Update your .env file with the path to the client_secret.json file

## Development

### Project Structure

- `app.py`: Main FastAPI application
- `calendar_service.py`: Google Calendar API operations
- `auth_utils.py`: OAuth authentication utilities
- `function_specs.py`: OpenAI function calling specifications
- `schemas.py`: Pydantic models for request/response validation

### Adding New Features

To add new calendar capabilities:

1. Add a new function in `calendar_service.py`
2. Add the corresponding function specification in `function_specs.py`
3. Update relevant Pydantic models in `schemas.py` if needed

## Security Considerations

- This implementation uses in-memory storage for OAuth states which is fine for development but not recommended for production
- For production, implement proper user authentication and secure storage for OAuth tokens in a database
- Update CORS settings in app.py to restrict allowed origins
- Consider implementing rate limiting for API endpoints

## License

[MIT License](LICENSE)
