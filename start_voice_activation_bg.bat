@echo off
title Starting Jarvis Voice Activation
cd /d "%~dp0"
echo Starting Jarvis Wake Word Listener in the background...
start pythonw wake_word_listener.py
exit
