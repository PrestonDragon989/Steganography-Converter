@echo off

:: Setting Title of window
if "%~1"=="" (
    title Steganography Converter
) else (
    title Steganography Converter (%1)
)

:: Check if the first argument is empty
if "%~1"=="" (
    "%~dp0main.exe" 
) else (
	:: title Steganography Converter (%1)
    "%~dp0main.exe" "%~1"
)

echo.
	
pause

exit