@echo off
REM Docker wrapper script for Zep MCP Server (Windows)

REM Get the directory of this script
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..

REM Load environment variables if .env exists
if exist "%PROJECT_DIR%\.env" (
    for /f "tokens=1,2 delims==" %%a in (%PROJECT_DIR%\.env) do (
        set %%a=%%b
    )
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker and try again.
    exit /b 1
)

REM Check if required environment variables are set
if "%ZEP_API_KEY%"=="" (
    echo Error: ZEP_API_KEY not set. Please copy env.example to .env and set your API key.
    exit /b 1
)
if "%ZEP_API_KEY%"=="your_zep_api_key_here" (
    echo Error: ZEP_API_KEY not set. Please copy env.example to .env and set your API key.
    exit /b 1
)

REM Set defaults for optional variables
if "%ZEP_USER_IDS%"=="" set ZEP_USER_IDS=aaron_whaley,tech_knowledge_base
if "%ZEP_DEFAULT_USER_ID%"=="" set ZEP_DEFAULT_USER_ID=aaron_whaley

REM Build the image if it doesn't exist
set IMAGE_NAME=zep-mcp-server
docker image inspect %IMAGE_NAME% >nul 2>&1
if errorlevel 1 (
    echo Building Docker image...
    docker build -t %IMAGE_NAME% "%PROJECT_DIR%"
)

REM Run the container with stdio transport
docker run --rm -i ^
    -e ZEP_API_KEY=%ZEP_API_KEY% ^
    -e ZEP_USER_IDS=%ZEP_USER_IDS% ^
    -e ZEP_DEFAULT_USER_ID=%ZEP_DEFAULT_USER_ID% ^
    -e TRANSPORT=stdio ^
    %IMAGE_NAME% python run_stdio.py 