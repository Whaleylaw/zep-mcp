# Multi-User Setup for Zep MCP Server

## Overview

The Zep MCP Server now supports multiple user IDs, allowing you to maintain separate memory contexts for different purposes (e.g., personal work vs. technical knowledge base) while maintaining the security of only allowing predefined user IDs.

## Configuration Changes Made

### 1. Updated Environment Variables

**Before:**
```json
{
  "env": {
    "ZEP_USER_ID": "aaron_whaley"
  }
}
```

**After:**
```json
{
  "env": {
    "ZEP_USER_IDS": "aaron_whaley,tech_knowledge_base",
    "ZEP_DEFAULT_USER_ID": "aaron_whaley"
  }
}
```

### 2. Updated Configuration Files

All MCP configuration files have been updated:
- `claude_desktop_config.json`
- `claude_code_config.json` 
- `cursor_mcp_config.json`
- `claude_mcp_config.json`

### 3. Enhanced Settings System

- **Multiple User IDs**: `ZEP_USER_IDS` accepts a comma-separated list
- **Default User ID**: `ZEP_DEFAULT_USER_ID` specifies which user ID to use by default
- **Validation**: Only predefined user IDs are accepted - invalid ones default to the configured default
- **Backwards Compatibility**: Existing code continues to work without changes

## How to Use

### 1. Creating Sessions with Specific User IDs

```python
# Create a session for personal use (uses default user ID)
create_smart_session_tool(
    context="personal project planning",
    context_type="coding",
    project="my_app"
)

# Create a session for technical knowledge base
create_smart_session_tool(
    context="technical documentation research", 
    context_type="research",
    project="knowledge_base",
    user_id="tech_knowledge_base"  # Specify the user ID
)
```

### 2. Available Tools with User ID Support

All enhanced memory tools now accept an optional `user_id` parameter:

- `create_smart_session_tool(user_id="tech_knowledge_base")`
- `get_relevant_context_tool(user_id="tech_knowledge_base")`
- `get_platform_summary_tool(user_id="tech_knowledge_base")`
- `get_facts_tool(user_id="tech_knowledge_base")`
- `list_sessions_tool(user_id="tech_knowledge_base")`

### 3. Utility Tools

- `get_available_user_ids_tool()`: View available user IDs and current default

## Security Features

1. **Whitelist Only**: Only user IDs in `ZEP_USER_IDS` are allowed
2. **Automatic Fallback**: Invalid user IDs automatically use the default
3. **Validation**: All user IDs are validated against the allowed list
4. **Logging**: Invalid attempts are logged for monitoring

## Example Use Cases

### Personal vs. Technical Knowledge

```bash
# Personal work
ZEP_USER_IDS="aaron_whaley,tech_knowledge_base"
ZEP_DEFAULT_USER_ID="aaron_whaley"
```

- `aaron_whaley`: Personal projects, general conversations
- `tech_knowledge_base`: Technical research, documentation, code examples

### Team vs. Individual Work

```bash
# Team environment
ZEP_USER_IDS="aaron_personal,team_shared"
ZEP_DEFAULT_USER_ID="aaron_personal"
```

- `aaron_personal`: Individual work and private notes
- `team_shared`: Shared team knowledge and collaborative work

## Testing the Setup

```bash
# Test the configuration
export ZEP_USER_IDS='aaron_whaley,tech_knowledge_base'
export ZEP_DEFAULT_USER_ID='aaron_whaley' 
export ZEP_API_KEY='your_api_key'

python -c "
from src.config.settings import Settings
s = Settings()
print('Available User IDs:', s.get_allowed_user_ids())
print('Default User ID:', s.default_user_id)
print('Validation - aaron_whaley:', s.is_valid_user_id('aaron_whaley'))
print('Validation - tech_knowledge_base:', s.is_valid_user_id('tech_knowledge_base'))
print('Validation - invalid_user:', s.is_valid_user_id('invalid_user'))
"
```

Expected output:
```
Available User IDs: ['aaron_whaley', 'tech_knowledge_base']
Default User ID: aaron_whaley
Validation - aaron_whaley: True
Validation - tech_knowledge_base: True
Validation - invalid_user: False
```

## Migration from Single User

**No migration needed!** The system is fully backwards compatible:

1. Existing sessions continue to work
2. Tools without `user_id` parameter use the default
3. All existing memory is preserved under the default user ID

## Switching User Contexts

To switch between user contexts, simply specify the `user_id` parameter in your tool calls:

```python
# Work in personal context
create_smart_session_tool(
    context="debugging my app",
    context_type="debugging"
    # No user_id = uses default (aaron_whaley)
)

# Work in technical knowledge context  
create_smart_session_tool(
    context="researching new framework",
    context_type="research",
    user_id="tech_knowledge_base"
)
```

You no longer need to manually edit JSON config files to switch contexts! 