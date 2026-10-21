@echo off
setlocal
echo ========================================================
echo   ComfyUI NVIDIA / CUDA High-Performance Startup Script
echo ========================================================

set PORT=8284

if exist venv\Scripts\python.exe (
    set PYTHON_EXE=venv\Scripts\python.exe
) else (
    set PYTHON_EXE=python
)

echo Starting ComfyUI on port %PORT% with CUDA acceleration...
%PYTHON_EXE% main.py --port %PORT% --disable-auto-launch --preview-method auto --gpu-only
pause
