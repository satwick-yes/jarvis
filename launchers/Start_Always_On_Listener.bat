@echo off
title Jarvis Always-On Voice Listener
color 0A
echo ===================================================
echo Jarvis Offline Voice Listener is running!
echo Do not close this window. Minimize it if you want.
echo Just say "Jarvis" to wake up the AI.
echo ===================================================
cd /d "C:\Users\satwi\Downloads\jarvis ai"
"C:\Users\satwi\AppData\Local\Programs\Python\Python312\python.exe" voice_activation\daemon.py
pause
