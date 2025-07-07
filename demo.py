#!/usr/bin/env python3
"""
Example usage of the Shazam music recognition system
"""

import os
import numpy as np
import wave
from shazam import Shazam

def create_sample_audio():
    """Create sample audio files for testing"""
    print("Creating sample audio files...")
    
    def generate_tone(frequency, duration, sample_rate=44100, amplitude=0.5):
        """Generate a pure tone"""
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        # Create a complex tone with harmonics
        wave = amplitude * np.sin(2 * np.pi * frequency * t)
        wave += 0.3 * amplitude * np.sin(2 * np.pi * frequency * 2 * t)  # Second harmonic
        wave += 0.2 * amplitude * np.sin(2 * np.pi * frequency * 3 * t)  # Third harmonic
        return (wave * 32767).astype(np.int16)
    
    def save_audio(audio_data, filename, sample_rate=44100):
        """Save audio data to WAV file"""
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())
    
    # Create sample songs with different frequency patterns
    samples = [
        ("sample_song_1.wav", "Happy Tune", "Test Artist", 440),  # A4
        ("sample_song_2.wav", "Sad Melody", "Test Artist", 523),  # C5
        ("sample_song_3.wav", "Rock Anthem", "Test Band", 329),   # E4
        ("sample_song_4.wav", "Jazz Standard", "Test Ensemble", 698),  # F5
    ]
    
    for filename, name, artist, base_freq in samples:
        # Create a more complex audio pattern
        duration = 15  # seconds
        audio = generate_tone(base_freq, duration)
        
        # Add some variation (simple melody)
        audio_2 = generate_tone(base_freq * 1.2, duration // 3)
        audio_3 = generate_tone(base_freq * 1.5, duration // 3)
        
        # Concatenate for a simple melody
        complex_audio = np.concatenate([audio[:len(audio)//3], audio_2, audio_3])
        
        save_audio(complex_audio, filename)
        print(f"Created {filename} - {name} by {artist}")
    
    return samples

def demo_basic_usage():
    """Demonstrate basic usage"""
    print("\n🎵 Shazam Demo - Basic Usage 🎵")
    print("=" * 40)
    
    # Initialize Shazam
    shazam = Shazam("demo_songs.db")
    
    try:
        # Create sample audio files
        samples = create_sample_audio()
        
        # Add songs to database
        print("\n📚 Adding songs to database...")
        for filename, name, artist, _ in samples:
            if os.path.exists(filename):
                song_id = shazam.add_song_to_database(filename, name, artist)
                if song_id:
                    print(f"✅ Added: {name} by {artist}")
        
        # List all songs
        print("\n📋 Songs in database:")
        shazam.list_songs()
        
        # Test identification
        print("\n🔍 Testing song identification...")
        test_file = samples[0][0]  # Use first sample
        result = shazam.identify_song(test_file)
        
        if result:
            name, artist, confidence = result
            print(f"✅ Identified: '{name}' by {artist} (confidence: {confidence})")
        else:
            print("❌ Could not identify the song")
        
        # Create a partial sample for testing
        print("\n🎤 Testing with partial audio...")
        create_partial_sample(test_file, "partial_sample.wav")
        result = shazam.identify_song("partial_sample.wav")
        
        if result:
            name, artist, confidence = result
            print(f"✅ Identified partial sample: '{name}' by {artist} (confidence: {confidence})")
        else:
            print("❌ Could not identify the partial sample")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        shazam.close()
        
        # Clean up demo files
        cleanup_files = [s[0] for s in samples] + ["partial_sample.wav", "demo_songs.db"]
        for f in cleanup_files:
            if os.path.exists(f):
                os.remove(f)
        print("\n🧹 Demo files cleaned up")

def create_partial_sample(source_file, output_file, start_sec=5, duration_sec=8):
    """Create a partial sample from a longer audio file"""
    try:
        with wave.open(source_file, 'rb') as wf:
            frames = wf.readframes(wf.getnframes())
            sample_rate = wf.getframerate()
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
        
        # Convert to numpy array
        audio = np.frombuffer(frames, dtype=np.int16)
        
        # Extract partial sample
        start_frame = int(start_sec * sample_rate)
        end_frame = int((start_sec + duration_sec) * sample_rate)
        partial_audio = audio[start_frame:end_frame]
        
        # Save partial sample
        with wave.open(output_file, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(sample_rate)
            wf.writeframes(partial_audio.tobytes())
        
        print(f"Created partial sample: {output_file}")
        
    except Exception as e:
        print(f"Error creating partial sample: {e}")

def demo_advanced_features():
    """Demonstrate advanced features"""
    print("\n🚀 Advanced Features Demo 🚀")
    print("=" * 40)
    
    shazam = Shazam("advanced_demo.db")
    
    try:
        # Create a test file
        samples = create_sample_audio()
        test_file = samples[0][0]
        
        # Add to database
        shazam.add_song_to_database(test_file, "Test Song", "Test Artist")
        
        # Demonstrate spectrogram visualization
        print("\n📊 Generating spectrogram...")
        print("Note: This will open a matplotlib window")
        try:
            shazam.visualize_spectrogram(test_file)
        except Exception as e:
            print(f"Visualization not available: {e}")
        
        # Show database info
        print("\n📈 Database statistics:")
        songs = shazam.db.get_all_songs()
        for song_id, name, artist, album, fingerprint_count in songs:
            print(f"Song: {name} - {fingerprint_count} fingerprints")
        
    except Exception as e:
        print(f"Error in advanced demo: {e}")
    
    finally:
        shazam.close()
        
        # Cleanup
        for f in [s[0] for s in samples] + ["advanced_demo.db"]:
            if os.path.exists(f):
                os.remove(f)

def interactive_demo():
    """Interactive demo mode"""
    print("\n🎮 Interactive Demo Mode 🎮")
    print("=" * 40)
    
    print("This demo will:")
    print("1. Create sample audio files")
    print("2. Add them to a database")
    print("3. Test identification")
    print("4. Clean up afterwards")
    
    input("\nPress Enter to continue...")
    
    demo_basic_usage()
    
    print("\nWould you like to see advanced features?")
    if input("(y/n): ").lower().startswith('y'):
        demo_advanced_features()

if __name__ == "__main__":
    interactive_demo()
