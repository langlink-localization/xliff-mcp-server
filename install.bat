@echo off
echo Installing XLIFF MCP Server...
echo ==============================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed. Please install Python 3.10 or higher.
    exit /b 1
)

echo √ Python found

REM Install the package
echo Installing dependencies...
python -m pip install -e .

echo.
echo √ Installation complete!
echo.
echo Testing the installation...
python test_server.py

echo.
echo ==============================
echo Setup Instructions for Claude Desktop:
echo.
echo Add the following to your Claude Desktop config file:
echo %AppData%\Claude\claude_desktop_config.json
echo.
echo {
echo   "mcpServers": {
echo     "xliff-processor": {
echo       "command": "python",
echo       "args": ["-m", "xliff_mcp.server"],
echo       "cwd": "%CD%"
echo     }
echo   }
echo }
echo.
echo Then restart Claude Desktop to use the XLIFF processor!
pause