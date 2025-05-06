from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    """Request model for the chat endpoint"""
    message: str = Field(..., description="User message text")
    user_id: str = Field(..., description="User identifier")

class ChatResponse(BaseModel):
    """Response model for the chat endpoint"""
    reply: str = Field(..., description="Assistant's response")
    
class AuthCallbackRequest(BaseModel):
    """Request model for the auth callback endpoint"""
    code: str = Field(..., description="Authorization code")
    state: str = Field(..., description="State parameter for OAuth verification")
    
class AuthResponse(BaseModel):
    """Response model for authentication requests"""
    status: str = Field(..., description="Authentication status")
    message: Optional[str] = None
    
class EventBase(BaseModel):
    """Base model for calendar events"""
    title: Optional[str] = None
    start: Optional[str] = None  # ISO timestamp
    end: Optional[str] = None    # ISO timestamp
    description: Optional[str] = None
    location: Optional[str] = None
    
class CreateEventRequest(EventBase):
    """Request model for creating calendar events"""
    title: str = Field(..., description="Event title")
    start: str = Field(..., description="Event start time (ISO format)")
    end: str = Field(..., description="Event end time (ISO format)")
    
class UpdateEventRequest(EventBase):
    """Request model for updating calendar events"""
    event_id: str = Field(..., description="ID of the event to update")
    
class DeleteEventRequest(BaseModel):
    """Request model for deleting calendar events"""
    event_id: str = Field(..., description="ID of the event to delete")
    
class ListEventsRequest(BaseModel):
    """Request model for listing calendar events"""
    start: str = Field(..., description="Start of time window (ISO format)")
    end: str = Field(..., description="End of time window (ISO format)")
    
class EventResponse(BaseModel):
    """Response model for calendar event operations"""
    status: str = Field(..., description="Operation status")
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None 