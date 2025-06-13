"""Session management tools for Zep MCP Server."""

import logging
from typing import Any, Dict, List, Optional

from zep_cloud.client import Zep
from zep_cloud import Session

logger = logging.getLogger(__name__)


async def create_session(
    client: Zep,
    session_id: str,
    user_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a new conversation session."""
    try:
        # FORCE aaron_whaley as user_id
        from ..config import settings
        if user_id != settings.default_user_id:
            logger.error(f"OVERRIDE: Forcing user_id from '{user_id}' to '{settings.default_user_id}'")
            user_id = settings.default_user_id
        
        # Handle metadata that might be passed as a string
        if isinstance(metadata, str):
            try:
                import json
                metadata = json.loads(metadata)
            except:
                # If it's not valid JSON, create a dict with the string as a value
                metadata = {"description": metadata}
        
        created_session = client.memory.add_session(
            session_id=session_id,
            user_id=user_id,
            metadata=metadata or {}
        )
        
        logger.info(f"Created session: {session_id} for user: {user_id}")
        return {
            "success": True,
            "session": {
                "session_id": created_session.session_id,
                "user_id": created_session.user_id,
                "metadata": created_session.metadata,
                "created_at": str(created_session.created_at) if hasattr(created_session, 'created_at') else None
            }
        }
    except Exception as e:
        logger.error(f"Error creating session {session_id}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


async def list_sessions(
    client: Zep,
    user_id: str,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """List user's conversation sessions."""
    try:
        sessions = client.user.get_sessions(user_id=user_id)
        
        logger.info(f"Retrieved {len(sessions)} sessions for user: {user_id}")
        return [
            {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "metadata": session.metadata,
                "created_at": str(session.created_at) if hasattr(session, 'created_at') else None,
                "updated_at": str(session.updated_at) if hasattr(session, 'updated_at') else None
            }
            for session in sessions
        ]
    except Exception as e:
        logger.error(f"Error listing sessions for user {user_id}: {str(e)}")
        return []