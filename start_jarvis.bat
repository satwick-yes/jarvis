@echo off
title Jarvis AI Assistant
cd /d "%~dp0"
echo Checking and installing dependencies...
pip install -r requirements.txt
echo Starting Jarvis AI...
python main.py
echo Jarvis has stopped or crashed.
pause
