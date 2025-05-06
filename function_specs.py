"""
OpenAI function specifications for calendar operations
"""

FUNCTION_SPECS = [
    {
        "name": "list_events",
        "description": "List calendar events in a given time window",
        "parameters": {
            "type": "object",
            "properties": {
                "start": {
                    "type": "string",
                    "description": "ISO timestamp for start of time window, e.g. 2023-11-15T00:00:00Z"
                },
                "end": {
                    "type": "string",
                    "description": "ISO timestamp for end of time window, e.g. 2023-11-15T23:59:59Z"
                }
            },
            "required": ["start", "end"]
        }
    },
    {
        "name": "create_event",
        "description": "Create a new calendar event",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title/summary of the event"
                },
                "start": {
                    "type": "string",
                    "description": "ISO timestamp for event start, e.g. 2023-11-15T10:00:00Z"
                },
                "end": {
                    "type": "string",
                    "description": "ISO timestamp for event end, e.g. 2023-11-15T11:00:00Z"
                },
                "description": {
                    "type": "string",
                    "description": "Optional detailed description of the event"
                },
                "location": {
                    "type": "string",
                    "description": "Optional location of the event"
                }
            },
            "required": ["title", "start", "end"]
        }
    },
    {
        "name": "update_event",
        "description": "Update an existing calendar event",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {
                    "type": "string",
                    "description": "ID of the event to update"
                },
                "title": {
                    "type": "string",
                    "description": "New title/summary of the event"
                },
                "start": {
                    "type": "string",
                    "description": "New ISO timestamp for event start"
                },
                "end": {
                    "type": "string",
                    "description": "New ISO timestamp for event end"
                },
                "description": {
                    "type": "string",
                    "description": "New detailed description of the event"
                },
                "location": {
                    "type": "string",
                    "description": "New location of the event"
                }
            },
            "required": ["event_id"]
        }
    },
    {
        "name": "delete_event",
        "description": "Delete a calendar event",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {
                    "type": "string",
                    "description": "ID of the event to delete"
                }
            },
            "required": ["event_id"]
        }
    }
] 