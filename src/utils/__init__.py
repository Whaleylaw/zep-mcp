"""Utility modules for Zep MCP Server."""

from .session_manager import (
    Platform,
    ContextType,
    detect_platform,
    create_smart_session,
    create_session_metadata,
    should_share_context,
    get_user_id
)

__all__ = [
    "Platform",
    "ContextType", 
    "detect_platform",
    "create_smart_session",
    "create_session_metadata",
    "should_share_context",
    "get_user_id"
]