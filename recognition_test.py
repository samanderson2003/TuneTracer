#!/usr/bin/env python3
"""
Comprehensive Song Recognition Test
This script demonstrates the full capabilities of the Shazam system
"""

import warnings
warnings.filterwarnings('ignore')

from shazam import Shazam
import numpy as np
import wave
import os

def create_distinctive_song(filename, duration=15, base_freq=440, pattern='simple'):
    """Create distinctive test songs with different patterns"""
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    if pattern == 'simple':
        # Simple sine wave with harmonics
        audio = (np.sin(2 * np.pi * base_freq * t) + 
                0.5 * np.sin(2 * np.pi * base_freq * 2 * t) + 
                0.3 * np.sin(2 * np.pi * base_freq * 3 * t))
    
    elif pattern == 'melody':
        # Create a simple melody
        notes = [base_freq, base_freq * 1.2, base_freq * 1.5, base_freq * 1.2]
        chunk_size = len(t) // len(notes)
        audio = np.zeros_like(t)
        
        for i, freq in enumerate(notes):
            start = i * chunk_size
            end = (i + 1) * chunk_size if i < len(notes) - 1 else len(t)
            chunk_t = t[start:end]
            audio[start:end] = (np.sin(2 * np.pi * freq * chunk_t) + 
                               0.3 * np.sin(2 * np.pi * freq * 2 * chunk_t))
    
    elif pattern == 'complex':
        # Complex pattern with frequency modulation
        mod_freq = 2  # Modulation frequency
        audio = np.sin(2 * np.pi * base_freq * t * (1 + 0.1 * np.sin(2 * np.pi * mod_freq * t)))
        audio += 0.3 * np.sin(2 * np.pi * base_freq * 1.5 * t)
    
    # Normalize and convert to 16-bit
    audio = audio / np.max(np.abs(audio)) * 0.8  # Prevent clipping
    audio = (audio * 32767).astype(np.int16)
    
    # Save to WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())
    
    return filename

def create_noisy_version(source_file, output_file, noise_level=0.1):
    """Create a noisy version of a song to test noise resistance"""
    with wave.open(source_file, 'rb') as wf:
        frames = wf.readframes(wf.getnframes())
        sample_rate = wf.getframerate()
    
    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
    
    # Add noise
    noise = np.random.normal(0, noise_level * np.std(audio), len(audio))
    noisy_audio = (audio + noise).astype(np.int16)
    
    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(noisy_audio.tobytes())
    
    return output_file

def create_partial_clip(source_file, output_file, start_sec=5, duration_sec=8):
    """Create a partial clip from a longer song"""
    with wave.open(source_file, 'rb') as wf:
        frames = wf.readframes(wf.getnframes())
        sample_rate = wf.getframerate()
    
    audio = np.frombuffer(frames, dtype=np.int16)
    start_frame = int(start_sec * sample_rate)
    end_frame = int((start_sec + duration_sec) * sample_rate)
    partial_audio = audio[start_frame:end_frame]
    
    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(partial_audio.tobytes())
    
    return output_file

def main():
    print("🎵 COMPREHENSIVE SONG RECOGNITION TEST 🎵")
    print("=" * 50)
    
    # Initialize Shazam
    shazam = Shazam('recognition_test.db')
    
    # Test songs data
    test_songs = [
        ('song1.wav', 'Harmonic Test Song', 'Test Artist', 440, 'simple'),
        ('song2.wav', 'Melody Test Song', 'Test Artist', 523, 'melody'),
        ('song3.wav', 'Complex Test Song', 'Test Artist', 329, 'complex'),
        ('song4.wav', 'High Frequency Song', 'Test Artist', 880, 'simple'),
    ]
    
    created_files = []
    
    try:
        # 1. Create and add test songs to database
        print("\n1. 📚 BUILDING SONG DATABASE")
        print("-" * 30)
        
        for filename, title, artist, freq, pattern in test_songs:
            print(f"Creating: {title}")
            create_distinctive_song(filename, duration=15, base_freq=freq, pattern=pattern)
            created_files.append(filename)
            
            song_id = shazam.add_song_to_database(filename, title, artist)
            if song_id:
                print(f"  ✅ Added to database with ID: {song_id}")
            else:
                print(f"  ❌ Failed to add to database")
        
        # 2. Test perfect recognition
        print("\n2. 🎯 TESTING PERFECT RECOGNITION")
        print("-" * 35)
        
        perfect_score = 0
        for filename, title, artist, _, _ in test_songs:
            result = shazam.identify_song(filename)
            if result:
                name, found_artist, confidence = result
                if name == title:
                    print(f"  ✅ {title}: PERFECT MATCH (confidence: {confidence})")
                    perfect_score += 1
                else:
                    print(f"  ⚠️  {title}: WRONG MATCH - found '{name}' (confidence: {confidence})")
            else:
                print(f"  ❌ {title}: NO MATCH FOUND")
        
        print(f"\nPerfect Recognition Score: {perfect_score}/{len(test_songs)}")
        
        # 3. Test partial recognition
        print("\n3. ✂️  TESTING PARTIAL RECOGNITION")
        print("-" * 35)
        
        partial_score = 0
        for filename, title, artist, _, _ in test_songs[:2]:  # Test first 2 songs
            partial_file = f"partial_{filename}"
            create_partial_clip(filename, partial_file, start_sec=4, duration_sec=7)
            created_files.append(partial_file)
            
            result = shazam.identify_song(partial_file)
            if result:
                name, found_artist, confidence = result
                if name == title:
                    print(f"  ✅ {title} (partial): MATCHED (confidence: {confidence})")
                    partial_score += 1
                else:
                    print(f"  ⚠️  {title} (partial): WRONG MATCH - found '{name}'")
            else:
                print(f"  ❌ {title} (partial): NO MATCH")
        
        print(f"\nPartial Recognition Score: {partial_score}/2")
        
        # 4. Test noise resistance
        print("\n4. 🔊 TESTING NOISE RESISTANCE")
        print("-" * 32)
        
        noise_score = 0
        for filename, title, artist, _, _ in test_songs[:2]:  # Test first 2 songs
            noisy_file = f"noisy_{filename}"
            create_noisy_version(filename, noisy_file, noise_level=0.2)
            created_files.append(noisy_file)
            
            result = shazam.identify_song(noisy_file)
            if result:
                name, found_artist, confidence = result
                if name == title:
                    print(f"  ✅ {title} (noisy): MATCHED (confidence: {confidence})")
                    noise_score += 1
                else:
                    print(f"  ⚠️  {title} (noisy): WRONG MATCH - found '{name}'")
            else:
                print(f"  ❌ {title} (noisy): NO MATCH")
        
        print(f"\nNoise Resistance Score: {noise_score}/2")
        
        # 5. Database summary
        print("\n5. 📊 DATABASE SUMMARY")
        print("-" * 25)
        shazam.list_songs()
        
        # 6. Overall results
        total_tests = len(test_songs) + 2 + 2  # perfect + partial + noise
        total_passed = perfect_score + partial_score + noise_score
        success_rate = (total_passed / total_tests) * 100
        
        print(f"\n6. 🏆 OVERALL RESULTS")
        print("-" * 22)
        print(f"Tests Passed: {total_passed}/{total_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 EXCELLENT - Song recognition is working very well!")
        elif success_rate >= 60:
            print("👍 GOOD - Song recognition is working well")
        elif success_rate >= 40:
            print("⚠️  FAIR - Song recognition has some issues")
        else:
            print("❌ POOR - Song recognition needs improvement")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    finally:
        # Cleanup
        shazam.close()
        for file in created_files + ['recognition_test.db']:
            if os.path.exists(file):
                os.remove(file)
        print("\n🧹 Cleanup completed")

if __name__ == "__main__":
    main()
