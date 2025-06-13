# Docker Setup Guide

This guide explains how to run the Zep MCP Server using Docker across Mac, Linux, and Windows machines. Docker provides a consistent environment and eliminates the need to install Python dependencies on each machine.

## 🚀 Quick Start

### 1. Prerequisites

- **Docker Desktop** installed on your machine:
  - **Mac**: [Docker Desktop for Mac](https://docs.docker.com/desktop/mac/install/)
  - **Windows**: [Docker Desktop for Windows](https://docs.docker.com/desktop/windows/install/)
  - **Linux**: [Docker Engine](https://docs.docker.com/engine/install/) or Docker Desktop

### 2. Setup Environment

1. **Copy environment template**:
   ```bash
   cp env.example .env
   ```

2. **Edit `.env` file** with your Zep API key:
   ```bash
   # Required: Your Zep Cloud API key
   ZEP_API_KEY=your_actual_zep_api_key_here
   
   # Multi-user configuration
   ZEP_USER_IDS=aaron_whaley,tech_knowledge_base
   ZEP_DEFAULT_USER_ID=aaron_whaley
   ```

### 3. Choose Your Deployment Method

## 🔄 Method 1: Direct Docker (Recommended for MCP Clients)

This method uses Docker as a command wrapper, maintaining the stdio transport that MCP clients expect.

### macOS/Linux Setup

1. **Make wrapper script executable**:
   ```bash
   chmod +x scripts/docker-wrapper.sh
   ```

2. **Configure MCP Client**:

   **Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "zep-memory": {
         "command": "/absolute/path/to/your/zep-mcp-server/scripts/docker-wrapper.sh",
         "args": [],
         "env": {}
       }
     }
   }
   ```

   **Cursor** (`~/Library/Application Support/Cursor/User/settings.json`):
   ```json
   {
     "mcp.servers": {
       "zep-memory": {
         "command": "/absolute/path/to/your/zep-mcp-server/scripts/docker-wrapper.sh",
         "args": [],
         "env": {}
       }
     }
   }
   ```

### Windows Setup

1. **Configure MCP Client**:

   **Claude Desktop** (`%APPDATA%\Claude\claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "zep-memory": {
         "command": "C:\\absolute\\path\\to\\your\\zep-mcp-server\\scripts\\docker-wrapper.bat",
         "args": [],
         "env": {}
       }
     }
   }
   ```

## 🌐 Method 2: Docker Compose (Recommended for Server Deployment)

This method runs the server as a persistent service with HTTP/SSE transport.

### 1. Start the Server

```bash
# Start the server
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the server
docker-compose down
```

### 2. Configure MCP Client for HTTP Transport

**Note**: This requires modifying the source code to support HTTP transport in MCP clients, or using the server for development/testing.

```bash
# Test the server
curl http://localhost:8052/health
```

## 🔧 Advanced Configuration

### Custom User IDs

Edit your `.env` file to customize user IDs:

```bash
# Add more user IDs (comma-separated)
ZEP_USER_IDS=personal,work,research,team_shared

# Set default
ZEP_DEFAULT_USER_ID=personal
```

### Port Configuration

For Method 2 (Docker Compose), you can change the port:

```bash
# In .env file
PORT=8053
```

Then update `docker-compose.yml`:
```yaml
ports:
  - "8053:8053"
```

### Build Custom Image

```bash
# Build with custom tag
docker build -t my-zep-mcp:latest .

# Use in docker-compose.yml
# image: my-zep-mcp:latest
```

## 🔍 Troubleshooting

### Common Issues

1. **Docker not running**:
   ```bash
   # Check Docker status
   docker info
   
   # Start Docker Desktop (GUI) or Docker daemon
   ```

2. **Permission denied on wrapper script**:
   ```bash
   # macOS/Linux
   chmod +x scripts/docker-wrapper.sh
   ```

3. **Environment variables not loaded**:
   ```bash
   # Verify .env file exists and has correct values
   cat .env
   
   # Test manually
   docker run --rm -e ZEP_API_KEY=your_key zep-mcp-server python -c "from src.config.settings import Settings; print(Settings().get_allowed_user_ids())"
   ```

4. **Container build fails**:
   ```bash
   # Clean build
   docker system prune -f
   docker build --no-cache -t zep-mcp-server .
   ```

### Viewing Logs

```bash
# Docker Compose
docker-compose logs zep-mcp-server

# Direct Docker
docker logs zep-mcp-server

# Follow logs in real-time
docker-compose logs -f
```

### Container Shell Access

```bash
# Access running container
docker exec -it zep-mcp-server /bin/bash

# Or start temporary container
docker run --rm -it zep-mcp-server /bin/bash
```

## 🚀 Benefits of Docker Deployment

### Consistency Across Platforms
- **Same Environment**: Identical Python version and dependencies everywhere
- **No Local Dependencies**: No need to install Python, pip, or packages
- **Version Control**: Lock to specific versions of everything

### Easy Management
- **Quick Updates**: `docker-compose pull && docker-compose up -d`
- **Easy Rollback**: Switch to previous image versions
- **Centralized Config**: Environment variables in one place

### Security
- **Isolated Environment**: Container isolation from host system
- **Non-root User**: Runs as unprivileged user inside container
- **No System Pollution**: Dependencies don't affect host system

### Multi-Machine Setup
- **Build Once, Run Everywhere**: Same image across all your machines
- **Shared Configuration**: Use same `.env` and compose files
- **Remote Deployment**: Can run on remote servers

## 📁 Docker File Structure

After setup, your project includes:

```
zep-mcp-server/
├── Dockerfile                           # Container definition
├── docker-compose.yml                   # Service orchestration
├── env.example                         # Environment template
├── .env                                # Your environment (create from template)
├── scripts/
│   ├── docker-wrapper.sh              # Unix wrapper script
│   └── docker-wrapper.bat             # Windows wrapper script
├── docker/
│   ├── claude_desktop_config.json     # Docker config for Claude Desktop (Unix)
│   ├── claude_desktop_config_windows.json # Docker config for Claude Desktop (Windows)
│   └── cursor_mcp_config.json         # Docker config for Cursor
└── logs/                               # Log files (created automatically)
```

## 🔄 Migration from Native Setup

If you're currently using a native Python installation:

1. **Backup current configs** (optional)
2. **Setup Docker environment** (follow Quick Start)
3. **Update MCP client configs** to use wrapper scripts
4. **Test functionality** with Docker setup
5. **Remove native installation** (optional)

The Docker setup is designed to be a drop-in replacement for the native installation.

## 🌍 Cross-Platform Notes

### Path Separators
- **Unix/macOS**: Use `/` in paths
- **Windows**: Use `\` in paths or escape as `\\`

### Script Extensions
- **Unix/macOS**: Use `.sh` scripts
- **Windows**: Use `.bat` scripts

### Example Configurations
Platform-specific examples are provided in the `docker/` directory.

This Docker setup provides a robust, consistent deployment method across all your machines! 🎉 