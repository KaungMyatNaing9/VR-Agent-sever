from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import logging

logger = logging.getLogger(__name__)

def list_events(creds_json: str, start: str, end: str) -> list:
    """
    List calendar events in a given time window.
    
    Args:
        creds_json: Google OAuth credentials as JSON string
        start: ISO timestamp for start of time window
        end: ISO timestamp for end of time window
        
    Returns:
        List of calendar events
    """
    try:
        credentials = Credentials.from_authorized_user_info(json.loads(creds_json))
        service = build("calendar", "v3", credentials=credentials)
        
        events_result = service.events().list(
            calendarId="primary",
            timeMin=start,
            timeMax=end,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        
        events = events_result.get("items", [])
        return events
    except HttpError as error:
        logger.error(f"Google Calendar API error: {error}")
        return {"error": f"Calendar API error: {str(error)}"}
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        return {"error": f"Failed to list events: {str(e)}"}

def create_event(creds_json: str, title: str, start: str, end: str, description: str = "", location: str = "") -> dict:
    """
    Create a new calendar event.
    
    Args:
        creds_json: Google OAuth credentials as JSON string
        title: Event title/summary
        start: ISO timestamp for event start
        end: ISO timestamp for event end
        description: Optional event description
        location: Optional event location
        
    Returns:
        Created event details
    """
    try:
        credentials = Credentials.from_authorized_user_info(json.loads(creds_json))
        service = build("calendar", "v3", credentials=credentials)
        
        event = {
            'summary': title,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end,
                'timeZone': 'UTC',
            },
        }
        
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return created_event
    except HttpError as error:
        logger.error(f"Google Calendar API error: {error}")
        return {"error": f"Calendar API error: {str(error)}"}
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        return {"error": f"Failed to create event: {str(e)}"}

def update_event(creds_json: str, event_id: str, title: str = None, start: str = None, 
                end: str = None, description: str = None, location: str = None) -> dict:
    """
    Update an existing calendar event.
    
    Args:
        creds_json: Google OAuth credentials as JSON string
        event_id: The ID of the event to update
        title: Optional new event title
        start: Optional new ISO timestamp for event start
        end: Optional new ISO timestamp for event end
        description: Optional new event description
        location: Optional new event location
        
    Returns:
        Updated event details
    """
    try:
        credentials = Credentials.from_authorized_user_info(json.loads(creds_json))
        service = build("calendar", "v3", credentials=credentials)
        
        # First get the existing event
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        # Update fields if provided
        if title:
            event['summary'] = title
        if description:
            event['description'] = description
        if location:
            event['location'] = location
        if start:
            event['start']['dateTime'] = start
        if end:
            event['end']['dateTime'] = end
            
        updated_event = service.events().update(
            calendarId='primary', 
            eventId=event_id, 
            body=event
        ).execute()
        
        return updated_event
    except HttpError as error:
        logger.error(f"Google Calendar API error: {error}")
        return {"error": f"Calendar API error: {str(error)}"}
    except Exception as e:
        logger.error(f"Error updating event: {e}")
        return {"error": f"Failed to update event: {str(e)}"}

def delete_event(creds_json: str, event_id: str) -> dict:
    """
    Delete a calendar event.
    
    Args:
        creds_json: Google OAuth credentials as JSON string
        event_id: The ID of the event to delete
        
    Returns:
        Status of deletion operation
    """
    try:
        credentials = Credentials.from_authorized_user_info(json.loads(creds_json))
        service = build("calendar", "v3", credentials=credentials)
        
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return {"status": "success", "message": f"Event {event_id} deleted successfully"}
    except HttpError as error:
        logger.error(f"Google Calendar API error: {error}")
        return {"error": f"Calendar API error: {str(error)}"}
    except Exception as e:
        logger.error(f"Error deleting event: {e}")
        return {"error": f"Failed to delete event: {str(e)}"} 