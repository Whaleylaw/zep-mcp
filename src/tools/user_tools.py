"""User management tools for Zep MCP Server."""

import logging
from typing import Any, Dict, Optional

from zep_cloud.client import Zep
from zep_cloud import User

logger = logging.getLogger(__name__)


async def create_user(
    client: Zep,
    user_id: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a new user in Zep Cloud."""
    try:
        created_user = client.user.add(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            metadata=metadata or {}
        )
        
        logger.info(f"Created user: {user_id}")
        return {
            "success": True,
            "user": {
                "user_id": created_user.user_id,
                "first_name": created_user.first_name,
                "last_name": created_user.last_name,
                "email": created_user.email,
                "metadata": created_user.metadata,
                "created_at": str(created_user.created_at) if hasattr(created_user, 'created_at') else None
            }
        }
    except Exception as e:
        logger.error(f"Error creating user {user_id}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


async def update_user_metadata(
    client: Zep,
    user_id: str,
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """Update user metadata."""
    try:
        # Get existing user to merge metadata
        user = client.user.get(user_id)
        
        # Merge metadata
        updated_metadata = {**(user.metadata or {}), **metadata}
        
        # Update user with merged metadata
        updated_user = client.user.update(
            user_id=user_id,
            metadata=updated_metadata
        )
        
        logger.info(f"Updated metadata for user: {user_id}")
        return {
            "success": True,
            "user": {
                "user_id": updated_user.user_id,
                "metadata": updated_user.metadata
            }
        }
    except Exception as e:
        logger.error(f"Error updating user metadata {user_id}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }