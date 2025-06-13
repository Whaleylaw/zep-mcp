"""Zep MCP Server - Main server implementation."""

from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from zep_cloud.client import Zep
from zep_cloud import Message, Session, User

from .config import settings
from .logging_config import setup_logging, get_logger
from .tools import (
    create_user,
    create_session,
    add_memory,
    get_memory,
    search_memory,
    get_facts,
    list_sessions,
    update_user_metadata
)
from .tools.enhanced_memory_tools import (
    get_relevant_context,
    create_smart_session_with_context,
    get_platform_summary
)
from .utils import ContextType

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Add file logging for debugging
import logging as std_logging
import os
log_file_path = os.path.join(os.path.expanduser('~'), 'zep_mcp_server.log')
file_handler = std_logging.FileHandler(log_file_path)
file_handler.setLevel(std_logging.DEBUG)
file_formatter = std_logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
std_logging.getLogger().addHandler(file_handler)

# Initialize FastMCP server
mcp = FastMCP("zep-memory-server")

# Initialize Zep client
zep_client = Zep(api_key=settings.zep_api_key)


@mcp.tool()
async def create_user_tool(
    user_id: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a new user in Zep Cloud.
    
    Args:
        user_id: Unique user identifier
        first_name: User's first name (recommended)
        last_name: User's last name (recommended)
        email: User's email address (recommended)
        metadata: Additional user metadata
        
    Returns:
        Created user object
    """
    # Validate user_id is in allowed list
    if not settings.is_valid_user_id(user_id):
        logger.warning(f"create_user_tool: Invalid user_id '{user_id}', using default: {settings.default_user_id}")
        user_id = settings.default_user_id
    
    return await create_user(
        zep_client, user_id, first_name, last_name, email, metadata
    )


@mcp.tool()
async def create_session_tool(
    session_id: str,
    user_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a new conversation session.
    
    Args:
        session_id: Unique session identifier
        user_id: User identifier for this session
        metadata: Additional session metadata
        
    Returns:
        Created session object
    """
    # Debug logging
    logger.warning(f"create_session_tool called with user_id: {user_id}")
    logger.warning(f"Allowed user_ids: {settings.get_allowed_user_ids()}")
    
    # Validate user_id is in allowed list
    if not settings.is_valid_user_id(user_id):
        logger.warning(f"Invalid user_id '{user_id}', using default: {settings.default_user_id}")
        user_id = settings.default_user_id
    
    return await create_session(zep_client, session_id, user_id, metadata)


@mcp.tool()
async def add_memory_tool(
    session_id: str,
    messages: List[Dict[str, Any]],
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Add conversation messages to user memory.
    
    Args:
        session_id: Session identifier
        messages: List of messages with role, content, and optional metadata
        user_id: User identifier (optional, for validation)
        
    Returns:
        Success status and stored message count
    """
    # Debug logging
    if user_id:
        logger.warning(f"add_memory_tool called with user_id: {user_id}")
        # Validate user_id is in allowed list
        if not settings.is_valid_user_id(user_id):
            logger.warning(f"Invalid user_id '{user_id}', using default: {settings.default_user_id}")
            user_id = settings.default_user_id
    
    return await add_memory(zep_client, session_id, messages, user_id)


@mcp.tool()
async def get_memory_tool(
    session_id: str,
    min_rating: float = 0.0,
    limit: int = 50
) -> Dict[str, Any]:
    """Retrieve memory for a session.
    
    Args:
        session_id: Session identifier
        min_rating: Minimum fact rating (0.0-1.0)
        limit: Maximum number of messages to return
        
    Returns:
        Memory context including facts, entities, and messages
    """
    return await get_memory(zep_client, session_id, min_rating, limit)


@mcp.tool()
async def search_memory_tool(
    session_id: str,
    query: str,
    limit: int = 10,
    search_scope: str = "messages"
) -> List[Dict[str, Any]]:
    """Search within a session's memory.
    
    Args:
        session_id: Session identifier
        query: Search query
        limit: Maximum results to return
        search_scope: Scope to search in ("messages", "summary", "facts")
        
    Returns:
        List of matching memory results with relevance scores
    """
    return await search_memory(zep_client, session_id, query, limit, search_scope)


@mcp.tool()
async def get_facts_tool(
    user_id: str,
    min_rating: float = 0.0
) -> List[Dict[str, Any]]:
    """Retrieve extracted facts about the user.
    
    Args:
        user_id: User identifier
        min_rating: Minimum fact rating (0.0-1.0)
        
    Returns:
        List of facts with ratings and metadata
    """
    # Validate user_id is in allowed list
    if not settings.is_valid_user_id(user_id):
        logger.warning(f"get_facts_tool: Invalid user_id '{user_id}', using default: {settings.default_user_id}")
        user_id = settings.default_user_id
    
    return await get_facts(zep_client, user_id, min_rating)


@mcp.tool()
async def list_sessions_tool(
    user_id: str,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """List user's conversation sessions.
    
    Args:
        user_id: User identifier
        limit: Maximum sessions to return
        
    Returns:
        List of user's sessions with metadata
    """
    # Validate user_id is in allowed list
    if not settings.is_valid_user_id(user_id):
        logger.warning(f"list_sessions_tool: Invalid user_id '{user_id}', using default: {settings.default_user_id}")
        user_id = settings.default_user_id
    
    return await list_sessions(zep_client, user_id, limit)


@mcp.tool()
async def update_user_metadata_tool(
    user_id: str,
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """Update user metadata.
    
    Args:
        user_id: User identifier
        metadata: Metadata to update (merged with existing)
        
    Returns:
        Updated user object
    """
    # Validate user_id is in allowed list
    if not settings.is_valid_user_id(user_id):
        logger.warning(f"update_user_metadata_tool: Invalid user_id '{user_id}', using default: {settings.default_user_id}")
        user_id = settings.default_user_id
    
    return await update_user_metadata(zep_client, user_id, metadata)


# Enhanced tools for multi-platform support

@mcp.tool()
async def get_relevant_context_tool(
    session_id: str,
    query: Optional[str] = None,
    limit: int = 10,
    lookback_days: int = 30,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Get relevant context from current and related sessions across platforms.
    
    Args:
        session_id: Current session identifier
        query: Optional search query for finding relevant memories
        limit: Maximum number of cross-session results
        lookback_days: How many days back to search
        user_id: Optional specific user ID to use (must be in allowed list)
        
    Returns:
        Combined context from current and related sessions
    """
    return await get_relevant_context(zep_client, session_id, query, limit, lookback_days, user_id)


@mcp.tool()
async def create_smart_session_tool(
    context: str,
    context_type: Optional[str] = "general",
    project: Optional[str] = None,
    initial_messages: Optional[List[Dict[str, str]]] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new session with intelligent naming and metadata.
    
    Args:
        context: Description of the session context
        context_type: Type of context (coding, general, research, deployment, debugging, documentation)
        project: Project name if applicable
        initial_messages: Optional initial messages to add
        user_id: Optional specific user ID to use (must be in allowed list)
        
    Returns:
        Created session information with platform detection
    """
    # Convert string context_type to enum
    try:
        context_type_enum = ContextType(context_type) if context_type else None
    except ValueError:
        context_type_enum = None
    
    return await create_smart_session_with_context(
        zep_client, context, context_type_enum, project, initial_messages, user_id
    )


@mcp.tool()
async def get_available_user_ids_tool() -> Dict[str, Any]:
    """Get the list of available user IDs.
    
    Returns:
        Information about available user IDs
    """
    return {
        "available_user_ids": settings.get_allowed_user_ids(),
        "default_user_id": settings.default_user_id,
        "description": "These are the allowed user IDs that can be used with the memory tools. Any other user ID will be replaced with the default."
    }


@mcp.tool()
async def get_platform_summary_tool(
    platform: Optional[str] = None,
    days: int = 7,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Get a summary of activity across platforms.
    
    Args:
        platform: Optional specific platform to filter by (cursor, claude_desktop, claude_code, web_claude)
        days: Number of days to look back
        user_id: Optional specific user ID to use (must be in allowed list)
        
    Returns:
        Summary of platform activity including sessions, contexts, and projects
    """
    return await get_platform_summary(zep_client, platform, days, user_id)


def main():
    """Run the MCP server."""
    logger.info(f"Starting Zep MCP Server")
    logger.info(f"Transport: {settings.transport}")
    
    # Run the server with the configured transport
    transport_kwargs = {}
    if settings.transport == "sse":
        transport_kwargs["host"] = settings.host
        transport_kwargs["port"] = settings.port
    
    mcp.run(transport=settings.transport, **transport_kwargs)


if __name__ == "__main__":
    main()