@echo off

:: Check if the first argument is empty
if "%~1"=="" (
    python3 "%~dp0main.py"
) else (
    python3 "%~dp0main.py" "%~1"
)

echo.

pause

exit