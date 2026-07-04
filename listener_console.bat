@echo off
title Jarvis Wake Word Listener (Console Mode)
cd /d "%~dp0"
echo ===================================================
echo Jarvis Wake Word Listener - Console Mode
echo ===================================================
echo.
echo Starting the microphone listener...
echo Say "jarvis wake up" to launch the main Jarvis UI.
echo You will see exactly what the microphone hears below.
echo.
python wake_word_listener.py
echo.
pause
