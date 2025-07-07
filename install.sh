#!/bin/bash

# Shazam Music Recognition System - Installation Script
# Compatible with macOS and Linux

echo "🎵 Installing Shazam Music Recognition System 🎵"
echo "=================================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Detect operating system
OS="$(uname -s)"
case "${OS}" in
    Darwin*)    
        echo "🍎 Detected macOS"
        
        # Check if Homebrew is installed
        if ! command -v brew &> /dev/null; then
            echo "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        echo "📦 Installing system dependencies with Homebrew..."
        brew install portaudio ffmpeg
        ;;
        
    Linux*)     
        echo "🐧 Detected Linux"
        
        # Check if apt is available (Debian/Ubuntu)
        if command -v apt-get &> /dev/null; then
            echo "📦 Installing system dependencies with apt..."
            sudo apt-get update
            sudo apt-get install -y python3-pyaudio portaudio19-dev ffmpeg python3-pip
        elif command -v yum &> /dev/null; then
            echo "📦 Installing system dependencies with yum..."
            sudo yum install -y python3-pyaudio portaudio-devel ffmpeg python3-pip
        else
            echo "⚠️  Unknown package manager. Please install manually:"
            echo "   - portaudio development libraries"
            echo "   - ffmpeg"
            echo "   - python3-pip"
        fi
        ;;
        
    CYGWIN*|MINGW32*|MSYS*|MINGW*)
        echo "🪟 Detected Windows"
        echo "Please install manually:"
        echo "1. Download and install ffmpeg from https://ffmpeg.org/"
        echo "2. Add ffmpeg to your PATH"
        echo "3. Install Python dependencies with: pip install -r requirements.txt"
        ;;
        
    *)          
        echo "❓ Unknown OS: ${OS}"
        echo "Please install portaudio and ffmpeg manually"
        ;;
esac

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# Test installation
echo "🧪 Testing installation..."
python3 -c "
import sys
try:
    import numpy, scipy, matplotlib, librosa, pydub
    print('✅ All core dependencies imported successfully')
    
    try:
        import pyaudio
        print('✅ PyAudio imported successfully')
    except ImportError:
        print('⚠️  PyAudio not available - recording may not work')
        
    print('🎉 Installation completed successfully!')
    print('')
    print('You can now run:')
    print('  python3 shazam.py      # Interactive mode')
    print('  python3 demo.py        # Run demo')
    print('  python3 test_shazam.py # Run tests')
    
except ImportError as e:
    print(f'❌ Import error: {e}')
    print('Some dependencies may not be installed correctly')
    sys.exit(1)
"

echo ""
echo "🎯 Installation script completed!"
