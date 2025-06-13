# Zep MCP Server

A Memory Context Protocol (MCP) server for Zep Cloud that provides intelligent memory management across multiple platforms like Cursor, Claude Desktop, and Claude Code.

## Features

- **Multi-Platform Memory**: Seamlessly share memory context across different AI interfaces
- **Smart Session Management**: Automatically creates sessions with intelligent naming and metadata
- **Cross-Platform Context**: Find relevant memories from related sessions
- **Multi-User Support**: Configure multiple user IDs for different memory contexts
- **Enhanced Search**: Semantic search across conversation history and facts

## Multi-User Configuration

The server supports multiple user IDs to allow for different memory contexts (e.g., personal vs. technical knowledge base).

**📖 For detailed multi-user setup and usage examples, see [MULTI_USER_SETUP.md](MULTI_USER_SETUP.md)**

### Environment Variables

Configure the following environment variables in your MCP config files:

- `ZEP_USER_IDS`: Comma-separated list of allowed user IDs (e.g., "aaron_whaley,tech_knowledge_base")
- `ZEP_DEFAULT_USER_ID`: Default user ID to use when none is specified (must be in the allowed list)
- `ZEP_API_KEY`: Your Zep Cloud API key

### Example Configuration

**claude_desktop_config.json:**
```json
{
  "mcpServers": {
    "zep-memory": {
      "command": "python",
      "args": ["/path/to/zep_mcp/run_stdio.py"],
      "env": {
        "ZEP_API_KEY": "your_zep_api_key",
        "ZEP_USER_IDS": "aaron_whaley,tech_knowledge_base",
        "ZEP_DEFAULT_USER_ID": "aaron_whaley"
      }
    }
  }
}
```

## Usage

### Creating Sessions with Specific User IDs

```python
# Create a session for personal use (default user)
create_smart_session_tool(
    context="personal project planning",
    context_type="general",
    project="my_app"
)

# Create a session for technical knowledge base
create_smart_session_tool(
    context="technical documentation research",
    context_type="research",
    project="knowledge_base",
    user_id="tech_knowledge_base"
)
```

### Available Tools

- `create_smart_session_tool`: Create intelligent sessions with optional user ID selection
- `get_relevant_context_tool`: Get context from current and related sessions
- `get_platform_summary_tool`: Get activity summary across platforms
- `get_available_user_ids_tool`: View available user IDs
- Standard Zep tools: `add_memory_tool`, `get_memory_tool`, `search_memory_tool`, etc.

### Key Features

1. **Security**: Only predefined user IDs are allowed - invalid IDs default to the configured default
2. **Flexibility**: Choose which user context to use per session
3. **Backward Compatibility**: Existing tools work without specifying user ID (uses default)
4. **Cross-Platform**: Memory context is shared across all platforms for the same user ID

## Installation

### Option 1: Native Python Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure your MCP client with the appropriate config file
4. Set your Zep API key and user IDs in the environment variables

### Option 2: Docker Deployment (Recommended for Multi-Platform)

Perfect for running consistently across Mac, Linux, and Windows machines:

1. **Install Docker Desktop** on your machine
2. **Clone and setup**:
   ```bash
   git clone https://github.com/yourusername/zep-mcp-server.git
   cd zep-mcp-server
   cp env.example .env
   # Edit .env with your Zep API key
   ```
3. **Use Docker wrapper in MCP configs**:
   - **Unix/Mac**: Point to `scripts/docker-wrapper.sh`
   - **Windows**: Point to `scripts/docker-wrapper.bat`

**📖 For complete Docker setup guide, see [DOCKER_SETUP.md](DOCKER_SETUP.md)**

## Development

### Running the Server Standalone

```bash
# For development with SSE transport
python run_server.py

# For MCP clients with stdio transport
python run_stdio.py
```

### Project Structure

```
zep-mcp-server/
├── src/
│   ├── server.py          # Main MCP server
│   ├── config/           # Configuration management
│   ├── tools/            # MCP tool implementations
│   └── utils/            # Utility functions
├── run_stdio.py          # STDIO transport runner
├── run_server.py         # SSE transport runner
├── requirements.txt      # Python dependencies
└── *.md                  # Documentation files
```

## Platform-Specific Notes

### Session Naming Convention

Sessions are automatically named using the pattern: `{platform}_{context}_{date}`

Examples:
- `cursor_debugging_api_2025_06_10`
- `claude_desktop_general_chat_2025_06_10`
- `claude_code_deployment_2025_06_10`

### Context Sharing

The system automatically shares context between sessions based on:
- **Same Project**: Sessions working on the same project share context
- **Related Context Types**: coding ↔ debugging, documentation ↔ research
- **Common Tags**: Sessions with overlapping metadata share context

### Platform Detection

The server automatically detects which platform is calling it through:
- Environment variables (`CURSOR_SESSION`, `CLAUDE_DESKTOP`, `CLAUDE_CODE`)
- Process information
- Configuration metadata

## Example Configurations

The repository includes example configuration files for each platform:

- `claude_desktop_config.json` - Claude Desktop configuration
- `claude_code_config.json` - Claude Code preferences  
- `cursor_mcp_config.json` - Cursor MCP configuration

Copy and modify these files according to your setup, replacing:
- `/path/to/your/zep_mcp/` with your actual paths
- `your_zep_api_key_here` with your Zep API key
- User IDs with your desired values

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp)
- Powered by [Zep Cloud](https://www.getzep.com/) for memory persistence
- Compatible with Anthropic's [Model Context Protocol](https://modelcontextprotocol.io/)

## Prerequisites

- Python 3.8+
- Zep Cloud API key (get one at [app.getzep.com](https://app.getzep.com/))
- MCP-compatible client (Claude Desktop, Claude Code, Cursor, etc.)

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/zep-mcp-server.git
cd zep-mcp-server

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the project root (optional, you can also use MCP config):

```env
# Required
ZEP_API_KEY=your_zep_api_key_here

# Multi-user support (optional)
ZEP_USER_IDS=aaron_whaley,tech_knowledge_base
ZEP_DEFAULT_USER_ID=aaron_whaley
```

### 3. Add to Your MCP Client

#### Claude Desktop

1. Open configuration file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Add the server configuration:

```json
{
  "mcpServers": {
    "zep-memory": {
      "command": "python",
      "args": [
        "/absolute/path/to/zep-mcp-server/run_stdio.py"
      ],
      "env": {
        "ZEP_API_KEY": "your_zep_api_key_here",
        "ZEP_USER_IDS": "aaron_whaley,tech_knowledge_base",
        "ZEP_DEFAULT_USER_ID": "aaron_whaley",
        "CLAUDE_DESKTOP": "true"
      }
    }
  }
}
```

**Note**: If you get a "spawn python ENOENT" error, use the full path to Python or your virtual environment's Python:
```json
"command": "/usr/bin/python3"
// or
"command": "/path/to/zep-mcp-server/venv/bin/python"
```

3. Restart Claude Desktop

#### Claude Code

1. Find your Claude Code configuration file:
   - macOS: `~/Library/Application Support/claude.ai/preferences.json`
   - Windows: `%APPDATA%\claude.ai\preferences.json`
   - Linux: `~/.config/claude.ai/preferences.json`

2. Add the Zep MCP server to the `mcpServers` section:

```json
{
  "mcpServers": {
    "zep-memory": {
      "command": "/path/to/python",
      "args": [
        "/path/to/zep-mcp-server/run_stdio.py"
      ],
      "env": {
        "ZEP_API_KEY": "your_zep_api_key_here",
        "ZEP_USER_IDS": "aaron_whaley,tech_knowledge_base",
        "ZEP_DEFAULT_USER_ID": "aaron_whaley",
        "CLAUDE_CODE": "true",
        "TRANSPORT": "stdio"
      }
    }
  }
}
```

**Important**: Claude Code requires the `TRANSPORT: "stdio"` environment variable.

3. Restart Claude Code

#### Cursor

1. Open Cursor Settings (`Cmd+,` on Mac, `Ctrl+,` on Windows/Linux)

2. Search for "MCP" or find the configuration file directly:
   - macOS: `~/Library/Application Support/Cursor/User/settings.json`
   - Windows: `%APPDATA%\Cursor\User\settings.json`
   - Linux: `~/.config/Cursor/User/settings.json`

3. Add to the `mcp.servers` section:

```json
{
  "mcp.servers": {
    "zep-memory": {
      "command": "/path/to/python",
      "args": [
        "/path/to/zep-mcp-server/run_stdio.py"
      ],
      "env": {
        "ZEP_API_KEY": "your_zep_api_key_here",
        "ZEP_USER_IDS": "aaron_whaley,tech_knowledge_base", 
        "ZEP_DEFAULT_USER_ID": "aaron_whaley",
        "CURSOR_SESSION": "true"
      }
    }
  }
}
```

4. Restart Cursor

## Usage Guide

### Important: Proper Session Creation

To ensure cross-platform memory sharing works correctly, **always create sessions using `create_smart_session_tool`** before adding memories:

1. **Create a Smart Session** (always do this first):
   ```
   Tool: create_smart_session_tool
   Arguments:
   - context: "Working on Zep MCP documentation"
   - context_type: "documentation"
   - project: "zep-mcp-server"
   ```

2. **Add Memories** (after session creation):
   ```
   Tool: add_memory_tool
   Arguments:
   - session_id: <from step 1>
   - messages: [conversation array]
   ```

### Available Tools

#### Session Management

- **create_smart_session_tool** - Creates a session with proper user ID and metadata
  - `context` (required): Description of the session purpose
  - `context_type`: One of: coding, general, research, deployment, debugging, documentation
  - `project`: Project name if applicable
  - `initial_messages`: Optional initial conversation
  - `user_id`: Optional user ID (defaults to configured default)

- **create_session_tool** - Basic session creation (use smart session instead)
  - `session_id` (required): Unique session identifier
  - `user_id` (required): User identifier
  - `metadata`: Additional session metadata

#### Memory Operations

- **add_memory_tool** - Add messages to a session
  - `session_id` (required): Target session
  - `messages` (required): Array of {role, content} objects
  - `user_id`: Optional, for validation

- **get_memory_tool** - Retrieve session memory
  - `session_id` (required): Session to retrieve
  - `min_rating`: Minimum fact rating (0.0-1.0)
  - `limit`: Maximum messages to return

- **search_memory_tool** - Search within a session
  - `session_id` (required): Session to search
  - `query` (required): Search query
  - `limit`: Maximum results
  - `search_scope`: One of: messages, summary, facts

#### User & Cross-Platform Tools

- **list_sessions_tool** - List all sessions for the user
  - `user_id` (required): User identifier
  - `limit`: Maximum sessions to return

- **get_relevant_context_tool** - Get context from related sessions
  - `session_id` (required): Current session
  - `query`: Optional search query
  - `limit`: Maximum cross-session results
  - `lookback_days`: How far back to search

- **get_platform_summary_tool** - See activity across platforms
  - `platform`: Filter by platform (cursor, claude_desktop, claude_code, web_claude)
  - `days`: Number of days to look back

## How It Works

1. **Unified User ID**: All platforms use the same user ID (configured via `ZEP_USER_ID`)
2. **Smart Sessions**: Sessions are named with pattern `platform_context_date`
3. **Platform Detection**: Automatically detects which client is being used
4. **Memory Persistence**: All conversations stored in Zep Cloud
5. **Context Sharing**: Related sessions share context based on metadata

## System Prompt for AI Assistants

**Important**: To ensure proper memory functionality, add the instructions from [`SYSTEM_PROMPT.md`](SYSTEM_PROMPT.md) to your AI assistant's system prompt or project instructions. This prevents common issues like hash user IDs and ensures cross-platform memory sharing works correctly.

## Troubleshooting

### Sessions showing hash user IDs

This happens when using `add_memory_tool` directly without first creating a session. Always use `create_smart_session_tool` first.

### Server not connecting

1. Ensure all paths in config files are absolute paths
2. Verify your Zep API key is correct
3. Check that Python and dependencies are installed
4. Look for errors in:
   - Claude Desktop: `~/Library/Logs/Claude/mcp-server-zep-memory.log`
   - Server logs: `~/zep_mcp_server.log`

### Memory not sharing across platforms

Ensure all platforms have the same `ZEP_USER_IDS` and `ZEP_DEFAULT_USER_ID` values in their configuration.