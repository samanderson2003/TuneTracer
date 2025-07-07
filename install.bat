@echo off
REM Shazam Music Recognition System - Windows Installation Script

echo 🎵 Installing Shazam Music Recognition System 🎵
echo ==================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not found in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
python --version

echo.
echo 📦 Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ⚠️  Manual steps required for Windows:
echo 1. Download FFmpeg from https://ffmpeg.org/download.html#build-windows
echo 2. Extract FFmpeg and add the bin folder to your system PATH
echo 3. Restart command prompt after adding to PATH

echo.
echo 🧪 Testing Python dependencies...
python -c "
import sys
try:
    import numpy, scipy, matplotlib, librosa, pydub
    print('✅ Core Python dependencies installed successfully')
    
    try:
        import pyaudio
        print('✅ PyAudio available')
    except ImportError:
        print('⚠️  PyAudio not available - you may need to install it manually')
        print('   Try: pip install pyaudio')
        
except ImportError as e:
    print('❌ Import error:', e)
    print('Some dependencies may not be installed correctly')
"

echo.
echo 🎯 Installation script completed!
echo.
echo You can now run:
echo   python shazam.py      # Interactive mode
echo   python demo.py        # Run demo
echo   python test_shazam.py # Run tests
echo.
pause
