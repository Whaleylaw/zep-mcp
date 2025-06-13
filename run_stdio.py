#!/usr/bin/env python
"""Run Zep MCP Server in stdio mode."""

import os
import sys
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Set stdio transport
os.environ["TRANSPORT"] = "stdio"

# Debug logging to file
debug_log_path = Path(__file__).parent / "mcp_debug.log"
logging.basicConfig(
    filename=str(debug_log_path),
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("=== Starting MCP Server ===")
logger.info(f"Python: {sys.executable}")
logger.info(f"CWD: {os.getcwd()}")
logger.info("Environment variables:")
for key in ["ZEP_API_KEY", "ZEP_USER_ID", "CLAUDE_DESKTOP", "TRANSPORT"]:
    value = os.environ.get(key)
    if key == "ZEP_API_KEY" and value:
        value = value[:10] + "..." if len(value) > 10 else value
    logger.info(f"  {key}: {value}")

from src.server import main

if __name__ == "__main__":
    main()