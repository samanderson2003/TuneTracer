#!/usr/bin/env python3
"""
Simple test script for the Shazam music recognition system
"""

import os
import sys
import numpy as np
from shazam import Shazam

def test_basic_functionality():
    """Test basic functionality with synthetic audio"""
    print("Testing Shazam functionality...")
    
    # Create a simple test audio file
    def create_test_audio(filename, duration=5, freq=440):
        """Create a simple sine wave audio file for testing"""
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        # Create a sine wave with some harmonics
        audio = np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 2 * t)
        audio = (audio * 32767).astype(np.int16)
        
        import wave
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio.tobytes())
        
        return filename
    
    try:
        # Initialize Shazam
        shazam = Shazam("test_songs.db")
        
        # Create test audio files
        print("Creating test audio files...")
        test_file1 = create_test_audio("test_song1.wav", duration=10, freq=440)  # A note
        test_file2 = create_test_audio("test_song2.wav", duration=10, freq=523)  # C note
        
        # Add songs to database
        print("Adding test songs to database...")
        shazam.add_song_to_database(test_file1, "Test Song A", "Test Artist", "Test Album")
        shazam.add_song_to_database(test_file2, "Test Song C", "Test Artist", "Test Album")
        
        # List songs
        print("\nListing songs in database:")
        shazam.list_songs()
        
        # Test identification
        print(f"\nTesting identification of {test_file1}...")
        result = shazam.identify_song(test_file1)
        if result:
            name, artist, confidence = result
            print(f"✅ Identified: '{name}' by {artist} (confidence: {confidence})")
        else:
            print("❌ Failed to identify song")
        
        # Clean up
        shazam.close()
        
        # Remove test files
        for f in [test_file1, test_file2, "test_songs.db"]:
            if os.path.exists(f):
                os.remove(f)
        
        print("\n✅ Basic test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_functionality()
