@echo off
cd /d "%~dp0"
start "RIBO Practice Portal Server" /min py server.py
timeout /t 2 /nobreak >nul
start "" http://127.0.0.1:8000