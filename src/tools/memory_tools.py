"""Memory management tools for Zep MCP Server."""

import logging
from typing import Any, Dict, List, Optional

from zep_cloud.client import Zep
from zep_cloud import Message

logger = logging.getLogger(__name__)


async def add_memory(
    client: Zep,
    session_id: str,
    messages: List[Dict[str, Any]],
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Add conversation messages to user memory."""
    try:
        # Convert message dicts to Message objects
        message_objects = []
        for msg in messages:
            message = Message(
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
                metadata=msg.get("metadata", {})
            )
            message_objects.append(message)
        
        # Add messages to memory
        client.memory.add(
            session_id=session_id,
            messages=message_objects
        )
        
        logger.info(f"Added {len(messages)} messages to session: {session_id}")
        return {
            "success": True,
            "messages_added": len(messages),
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"Error adding memory to session {session_id}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


async def get_memory(
    client: Zep,
    session_id: str,
    min_rating: float = 0.0,
    limit: int = 50
) -> Dict[str, Any]:
    """Retrieve memory for a session."""
    try:
        memory = client.memory.get(session_id)
        
        # Extract data from memory object
        result = {
            "success": True,
            "session_id": session_id,
            "messages": []
        }
        
        # Add messages if available
        if hasattr(memory, 'messages') and memory.messages:
            result["messages"] = [
                {
                    "role": msg.role,
                    "role_type": msg.role_type.value if hasattr(msg.role_type, 'value') else str(msg.role_type),
                    "content": msg.content,
                    "metadata": msg.metadata
                }
                for msg in memory.messages[:limit]
            ]
        
        # Add other memory components if available
        if hasattr(memory, 'context'):
            result["context"] = memory.context
        
        if hasattr(memory, 'facts') and memory.facts:
            # Filter facts by rating
            facts = []
            for f in memory.facts:
                # Check if f is an object with rating attribute
                if hasattr(f, 'rating') and hasattr(f, 'fact'):
                    if f.rating >= min_rating:
                        facts.append({
                            "fact": f.fact,
                            "rating": f.rating,
                            "created_at": str(f.created_at) if hasattr(f, 'created_at') else None
                        })
                elif isinstance(f, str):
                    # If fact is just a string, include it without rating filter
                    facts.append({
                        "fact": f,
                        "rating": None,
                        "created_at": None
                    })
            result["facts"] = facts
        
        if hasattr(memory, 'summary') and memory.summary:
            result["summary"] = {
                "content": memory.summary.content if hasattr(memory.summary, 'content') else str(memory.summary)
            }
        
        logger.info(f"Retrieved memory for session: {session_id}")
        return result
    except Exception as e:
        logger.error(f"Error getting memory for session {session_id}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


async def search_memory(
    client: Zep,
    session_id: str,
    query: str,
    limit: int = 10,
    search_scope: str = "messages"
) -> List[Dict[str, Any]]:
    """Search within a session's memory."""
    try:
        # Use the search method with session_id and query
        results = client.memory.search(
            session_id=session_id,
            text=query,
            search_scope=search_scope,
            limit=limit
        )
        
        logger.info(f"Searched memories for session {session_id} with query: {query}")
        return [
            {
                "message": {
                    "role": result.message.role,
                    "content": result.message.content,
                    "metadata": result.message.metadata if hasattr(result.message, 'metadata') else {}
                },
                "score": result.score if hasattr(result, 'score') else 0.0,
                "session_id": result.session_id if hasattr(result, 'session_id') else None
            }
            for result in results
        ]
    except Exception as e:
        logger.error(f"Error searching memory for user {user_id}: {str(e)}")
        return []


async def get_facts(
    client: Zep,
    user_id: str,
    min_rating: float = 0.0
) -> List[Dict[str, Any]]:
    """Retrieve extracted facts about the user."""
    try:
        # Get facts for user
        facts_response = client.user.get_facts(user_id=user_id)
        facts = []
        
        # Check if response has facts
        if hasattr(facts_response, 'facts') and facts_response.facts:
            # Filter by rating
            filtered_facts = [
                f for f in facts_response.facts 
                if f.rating >= min_rating
            ]
            
            facts = [
                {
                    "fact": f.fact,
                    "rating": f.rating,
                    "source": f.source if hasattr(f, 'source') else None,
                    "created_at": str(f.created_at) if hasattr(f, 'created_at') else None,
                    "metadata": f.metadata if hasattr(f, 'metadata') else {}
                }
                for f in filtered_facts
            ]
        
        logger.info(f"Retrieved {len(facts)} facts for user: {user_id}")
        return facts
    except Exception as e:
        logger.error(f"Error getting facts for user {user_id}: {str(e)}")
        return []