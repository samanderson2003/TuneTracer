#!/usr/bin/env python3
"""
Warning-free startup script for Shazam music recognition system
This script suppresses common warnings and provides a clean user experience
"""

import warnings
import os
import sys

# Suppress all warnings for clean output
warnings.filterwarnings('ignore')

# Suppress specific library warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Set environment variables to suppress warnings
os.environ['PYTHONWARNINGS'] = 'ignore'

# Suppress PyAudio warnings on macOS
if sys.platform == 'darwin':
    os.environ['PA_ALSA_PLUGHW'] = '0'

# Import and run the main Shazam application
try:
    from shazam import main
    if __name__ == "__main__":
        main()
except ImportError:
    print("Error: Could not import shazam module")
    print("Make sure all dependencies are installed:")
    print("  pip install numpy pyaudio matplotlib scipy librosa pydub")
except Exception as e:
    print(f"Error starting Shazam: {e}")
