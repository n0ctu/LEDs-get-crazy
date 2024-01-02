@echo off

REM Activate the virtual environment
CALL "%~dp0venv\Scripts\activate"

REM Start the web component
python.exe "%~dp0webapp-dev.py"

pause