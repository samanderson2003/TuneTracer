#!/usr/bin/env python3
"""
Setup script for Shazam-like Music Recognition System
"""

import subprocess
import sys
import os

def install_system_dependencies():
    """Install system dependencies based on the operating system"""
    print("Installing system dependencies...")
    
    if sys.platform == "darwin":  # macOS
        print("Detected macOS - installing with Homebrew...")
        try:
            # Check if brew is installed
            subprocess.run(["brew", "--version"], check=True, capture_output=True)
            
            # Install portaudio and ffmpeg
            subprocess.run(["brew", "install", "portaudio", "ffmpeg"], check=True)
            print("✅ System dependencies installed successfully!")
            
        except subprocess.CalledProcessError:
            print("❌ Homebrew not found. Please install Homebrew first:")
            print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            return False
        except FileNotFoundError:
            print("❌ Homebrew not found. Please install Homebrew first.")
            return False
            
    elif sys.platform.startswith("linux"):  # Linux
        print("Detected Linux - installing with apt...")
        try:
            subprocess.run([
                "sudo", "apt-get", "update"
            ], check=True)
            
            subprocess.run([
                "sudo", "apt-get", "install", "-y",
                "python3-pyaudio", "portaudio19-dev", "ffmpeg"
            ], check=True)
            print("✅ System dependencies installed successfully!")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install system dependencies: {e}")
            return False
            
    elif sys.platform == "win32":  # Windows
        print("Detected Windows")
        print("Please manually install:")
        print("1. FFmpeg from https://ffmpeg.org/download.html")
        print("2. Add FFmpeg to your PATH")
        print("Python dependencies will be installed automatically.")
        
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], check=True)
        
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        
        print("✅ Python dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False

def test_installation():
    """Test if all dependencies are working"""
    print("Testing installation...")
    
    try:
        # Test imports
        import numpy
        print("✅ NumPy imported successfully")
        
        import scipy
        print("✅ SciPy imported successfully")
        
        import matplotlib
        print("✅ Matplotlib imported successfully")
        
        import librosa
        print("✅ Librosa imported successfully")
        
        import pydub
        print("✅ Pydub imported successfully")
        
        try:
            import pyaudio
            print("✅ PyAudio imported successfully")
        except ImportError:
            print("⚠️  PyAudio import failed - audio recording may not work")
            
        print("✅ All core dependencies are working!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main setup function"""
    print("🎵 Shazam-like Music Recognition System Setup 🎵")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install system dependencies
    if not install_system_dependencies():
        print("⚠️  System dependencies installation failed")
        print("You may need to install them manually")
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Setup failed")
        sys.exit(1)
    
    # Test installation
    if test_installation():
        print("\n🎉 Setup completed successfully!")
        print("\nYou can now run:")
        print("  python shazam.py        # Interactive mode")
        print("  python test_shazam.py   # Run tests")
    else:
        print("\n❌ Setup completed with errors")
        print("Some features may not work properly")

if __name__ == "__main__":
    main()
