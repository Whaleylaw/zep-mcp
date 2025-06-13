"""Smart session management for multi-platform memory continuity."""

import os
import sys
from datetime import datetime
from typing import Dict, Optional, Any, List
from enum import Enum

class Platform(Enum):
    """Supported platforms."""
    CURSOR = "cursor"
    CLAUDE_DESKTOP = "claude_desktop"
    CLAUDE_CODE = "claude_code"
    WEB_CLAUDE = "web_claude"
    UNKNOWN = "unknown"

class ContextType(Enum):
    """Types of contexts."""
    CODING = "coding"
    GENERAL = "general"
    RESEARCH = "research"
    DEPLOYMENT = "deployment"
    DEBUGGING = "debugging"
    DOCUMENTATION = "documentation"

def detect_platform() -> Platform:
    """Detect which platform is running the MCP server."""
    # Check environment variables
    if os.environ.get("CURSOR_SESSION"):
        return Platform.CURSOR
    if os.environ.get("CLAUDE_DESKTOP"):
        return Platform.CLAUDE_DESKTOP
    if os.environ.get("CLAUDE_CODE"):
        return Platform.CLAUDE_CODE
    
    # Check process name
    process_name = sys.argv[0].lower() if sys.argv else ""
    if "cursor" in process_name:
        return Platform.CURSOR
    if "claude" in process_name and "desktop" in process_name:
        return Platform.CLAUDE_DESKTOP
    if "claude" in process_name and "code" in process_name:
        return Platform.CLAUDE_CODE
    
    # Check parent process or other indicators
    parent_process = os.environ.get("PARENT_PROCESS", "").lower()
    if "cursor" in parent_process:
        return Platform.CURSOR
    if "claude" in parent_process:
        if "desktop" in parent_process:
            return Platform.CLAUDE_DESKTOP
        elif "code" in parent_process:
            return Platform.CLAUDE_CODE
    
    # Default to web claude or unknown
    return Platform.WEB_CLAUDE

def create_smart_session(
    context: str, 
    context_type: Optional[ContextType] = None,
    project: Optional[str] = None
) -> str:
    """
    Create a smart session ID with platform and context information.
    
    Args:
        context: Brief description of the session context
        context_type: Type of context (coding, general, etc.)
        project: Optional project name
        
    Returns:
        Session ID in format: platform_context_date
    """
    platform = detect_platform()
    date = datetime.now().strftime("%Y_%m_%d")
    
    # Clean context for use in ID
    context_clean = context.lower().replace(" ", "_").replace("-", "_")[:20]
    
    # Build session ID
    session_id = f"{platform.value}_{context_clean}_{date}"
    
    return session_id

def create_session_metadata(
    context: str,
    context_type: Optional[ContextType] = None,
    project: Optional[str] = None,
    privacy_level: str = "normal",
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create rich metadata for a session.
    
    Args:
        context: Description of the session context
        context_type: Type of context
        project: Project name if applicable
        privacy_level: Privacy level (normal, sensitive)
        tags: Additional tags for the session
        
    Returns:
        Metadata dictionary
    """
    platform = detect_platform()
    
    metadata = {
        "platform": platform.value,
        "context": context,
        "context_type": context_type.value if context_type else "general",
        "created_at": datetime.now().isoformat(),
        "privacy_level": privacy_level
    }
    
    if project:
        metadata["project"] = project
    
    if tags:
        metadata["tags"] = tags
    
    # Add platform-specific metadata
    if platform == Platform.CURSOR:
        metadata["editor"] = "cursor"
        metadata["primary_use"] = "coding"
    elif platform == Platform.CLAUDE_DESKTOP:
        metadata["interface"] = "desktop"
        metadata["primary_use"] = "general"
    elif platform == Platform.CLAUDE_CODE:
        metadata["interface"] = "cli"
        metadata["primary_use"] = "coding"
    
    return metadata

def should_share_context(
    current_session_metadata: Dict[str, Any],
    other_session_metadata: Dict[str, Any]
) -> bool:
    """
    Determine if context should be shared between two sessions.
    
    Args:
        current_session_metadata: Metadata of current session
        other_session_metadata: Metadata of another session
        
    Returns:
        True if context should be shared
    """
    # Don't share sensitive sessions
    if (current_session_metadata.get("privacy_level") == "sensitive" or 
        other_session_metadata.get("privacy_level") == "sensitive"):
        return False
    
    # Share if same project
    if (current_session_metadata.get("project") and 
        current_session_metadata.get("project") == other_session_metadata.get("project")):
        return True
    
    # Share if related context types
    current_type = current_session_metadata.get("context_type", "general")
    other_type = other_session_metadata.get("context_type", "general")
    
    # Define related context types
    related_contexts = {
        "coding": ["debugging", "deployment", "documentation"],
        "debugging": ["coding", "deployment"],
        "deployment": ["coding", "debugging"],
        "documentation": ["coding", "research"],
        "research": ["documentation", "general"],
        "general": ["research"]
    }
    
    if current_type in related_contexts.get(other_type, []):
        return True
    if other_type in related_contexts.get(current_type, []):
        return True
    
    # Share if common tags
    current_tags = set(current_session_metadata.get("tags", []))
    other_tags = set(other_session_metadata.get("tags", []))
    if current_tags and other_tags and current_tags.intersection(other_tags):
        return True
    
    return False

def get_user_id(user_id: Optional[str] = None) -> str:
    """
    Get a validated user ID.
    
    Args:
        user_id: Optional specific user ID to validate and use
        
    Returns:
        Validated user ID (either provided and validated, or default)
        
    Raises:
        ValueError: If provided user_id is not in allowed list
    """
    from ..config import settings
    
    if user_id is None:
        return settings.default_user_id
    
    if not settings.is_valid_user_id(user_id):
        raise ValueError(f"User ID '{user_id}' is not in allowed list: {settings.allowed_user_ids}")
    
    return user_id