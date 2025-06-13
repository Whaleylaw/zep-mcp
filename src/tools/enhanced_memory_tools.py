"""Enhanced memory tools with cross-platform context awareness."""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from zep_cloud.client import Zep
from zep_cloud import Message

from ..utils import (
    get_user_id, 
    should_share_context,
    create_smart_session,
    create_session_metadata,
    ContextType
)

logger = logging.getLogger(__name__)

async def get_relevant_context(
    client: Zep,
    current_session_id: str,
    query: Optional[str] = None,
    limit: int = 10,
    lookback_days: int = 30,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get relevant context from current session and related sessions.
    
    Args:
        client: Zep client
        current_session_id: Current session ID
        query: Optional search query for finding relevant memories
        limit: Maximum number of cross-session results
        lookback_days: How many days back to search
        user_id: Optional specific user ID to use
        
    Returns:
        Combined context from current and related sessions
    """
    try:
        validated_user_id = get_user_id(user_id)
        result = {
            "current_session": {},
            "related_sessions": [],
            "cross_platform_insights": []
        }
        
        # Get current session memory
        try:
            current_memory = client.memory.get(session_id=current_session_id)
            result["current_session"] = {
                "session_id": current_session_id,
                "messages": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "created_at": str(msg.created_at) if hasattr(msg, 'created_at') else None
                    }
                    for msg in (current_memory.messages or [])[-20:]  # Last 20 messages
                ],
                "summary": str(current_memory.summary) if hasattr(current_memory, 'summary') and current_memory.summary else None
            }
        except Exception as e:
            logger.warning(f"Could not get current session memory: {e}")
        
        # Get all user sessions
        try:
            all_sessions = client.user.get_sessions(user_id=validated_user_id)
            
            # Filter sessions by date
            cutoff_date = datetime.now() - timedelta(days=lookback_days)
            recent_sessions = []
            
            for session in all_sessions:
                # Skip current session
                if session.session_id == current_session_id:
                    continue
                
                # Check if session is recent enough
                if hasattr(session, 'created_at') and session.created_at:
                    session_date = session.created_at
                    if isinstance(session_date, str):
                        session_date = datetime.fromisoformat(session_date.replace('Z', '+00:00'))
                    if session_date < cutoff_date:
                        continue
                
                recent_sessions.append(session)
            
            # Get current session metadata
            current_metadata = {}
            for session in all_sessions:
                if session.session_id == current_session_id:
                    current_metadata = session.metadata or {}
                    break
            
            # Find related sessions based on metadata
            related_sessions = []
            for session in recent_sessions:
                other_metadata = session.metadata or {}
                if should_share_context(current_metadata, other_metadata):
                    related_sessions.append(session)
            
            # Search for relevant memories across related sessions
            if query and related_sessions:
                for session in related_sessions[:5]:  # Limit to 5 related sessions
                    try:
                        search_results = client.memory.search(
                            session_id=session.session_id,
                            text=query,
                            search_scope="messages",
                            limit=3
                        )
                        
                        if search_results:
                            result["related_sessions"].append({
                                "session_id": session.session_id,
                                "platform": session.metadata.get("platform", "unknown") if session.metadata else "unknown",
                                "context": session.metadata.get("context", "unknown") if session.metadata else "unknown",
                                "relevant_memories": [
                                    {
                                        "content": res.message.content if hasattr(res, 'message') else str(res),
                                        "score": res.score if hasattr(res, 'score') else 0.0
                                    }
                                    for res in search_results[:2]
                                ]
                            })
                    except Exception as e:
                        logger.debug(f"Could not search session {session.session_id}: {e}")
            
            # Generate cross-platform insights
            platforms_used = set()
            projects_mentioned = set()
            contexts_covered = set()
            
            for session in all_sessions:
                if session.metadata:
                    platforms_used.add(session.metadata.get("platform", "unknown"))
                    if session.metadata.get("project"):
                        projects_mentioned.add(session.metadata.get("project"))
                    contexts_covered.add(session.metadata.get("context_type", "general"))
            
            result["cross_platform_insights"] = {
                "platforms_active": list(platforms_used),
                "projects_in_progress": list(projects_mentioned),
                "context_types": list(contexts_covered),
                "total_sessions": len(all_sessions),
                "recent_sessions": len(recent_sessions)
            }
            
        except Exception as e:
            logger.error(f"Error getting related context: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in get_relevant_context: {e}")
        return {
            "error": str(e),
            "current_session": {},
            "related_sessions": [],
            "cross_platform_insights": []
        }

async def create_smart_session_with_context(
    client: Zep,
    context: str,
    context_type: Optional[ContextType] = None,
    project: Optional[str] = None,
    initial_messages: Optional[List[Dict[str, str]]] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new session with smart naming and metadata.
    
    Args:
        client: Zep client
        context: Description of the session context
        context_type: Type of context
        project: Project name if applicable
        initial_messages: Optional initial messages to add
        user_id: Optional specific user ID to use
        
    Returns:
        Created session information
    """
    try:
        validated_user_id = get_user_id(user_id)
        
        # Generate smart session ID and metadata
        session_id = create_smart_session(context, context_type, project)
        metadata = create_session_metadata(context, context_type, project)
        
        # Create the session
        created_session = client.memory.add_session(
            session_id=session_id,
            user_id=validated_user_id,
            metadata=metadata
        )
        
        # Add initial messages if provided
        if initial_messages:
            message_objects = [
                Message(
                    role=msg.get("role", "user"),
                    content=msg.get("content", "")
                )
                for msg in initial_messages
            ]
            client.memory.add(
                session_id=session_id,
                messages=message_objects
            )
        
        logger.info(f"Created smart session: {session_id} for user: {validated_user_id}")
        
        return {
            "success": True,
            "session": {
                "session_id": session_id,
                "user_id": validated_user_id,
                "metadata": metadata,
                "platform": metadata.get("platform"),
                "context_type": metadata.get("context_type"),
                "project": metadata.get("project")
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating smart session: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def get_platform_summary(
    client: Zep,
    platform: Optional[str] = None,
    days: int = 7,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get a summary of activity across platforms.
    
    Args:
        client: Zep client
        platform: Optional specific platform to filter by
        days: Number of days to look back
        user_id: Optional specific user ID to use
        
    Returns:
        Summary of platform activity
    """
    try:
        validated_user_id = get_user_id(user_id)
        all_sessions = client.user.get_sessions(user_id=validated_user_id)
        
        cutoff_date = datetime.now() - timedelta(days=days)
        platform_stats = {}
        
        for session in all_sessions:
            # Check date
            if hasattr(session, 'created_at') and session.created_at:
                session_date = session.created_at
                if isinstance(session_date, str):
                    session_date = datetime.fromisoformat(session_date.replace('Z', '+00:00'))
                if session_date < cutoff_date:
                    continue
            
            # Get platform from metadata
            session_platform = "unknown"
            if session.metadata and "platform" in session.metadata:
                session_platform = session.metadata["platform"]
            
            # Filter by platform if specified
            if platform and session_platform != platform:
                continue
            
            # Update stats
            if session_platform not in platform_stats:
                platform_stats[session_platform] = {
                    "sessions": 0,
                    "contexts": set(),
                    "projects": set()
                }
            
            platform_stats[session_platform]["sessions"] += 1
            
            if session.metadata:
                if "context_type" in session.metadata:
                    platform_stats[session_platform]["contexts"].add(session.metadata["context_type"])
                if "project" in session.metadata:
                    platform_stats[session_platform]["projects"].add(session.metadata["project"])
        
        # Convert sets to lists for JSON serialization
        for plat in platform_stats:
            platform_stats[plat]["contexts"] = list(platform_stats[plat]["contexts"])
            platform_stats[plat]["projects"] = list(platform_stats[plat]["projects"])
        
        return {
            "period_days": days,
            "platforms": platform_stats,
            "total_sessions": sum(p["sessions"] for p in platform_stats.values()),
            "user_id": validated_user_id
        }
        
    except Exception as e:
        logger.error(f"Error getting platform summary: {e}")
        return {
            "error": str(e),
            "platforms": {},
            "total_sessions": 0
        }