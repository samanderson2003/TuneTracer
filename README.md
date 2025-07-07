# 🎵 TuneTrancer - Music Recognition System

A Python implementation of a music recognition system that can identify songs by analyzing their audio fingerprints.

## Features

- **Audio Recording**: Record audio directly from your microphone
- **Music Identification**: Identify songs from recorded audio or audio files
- **Database Management**: Store and manage songs with their audio fingerprints
- **Multiple Audio Formats**: Support for WAV, MP3, and other common audio formats
- **Spectrogram Visualization**: Visualize audio spectrograms
- **Interactive CLI**: Easy-to-use command-line interface

## How It Works

The system uses audio fingerprinting techniques similar to Shazam:

1. **Audio Processing**: Converts audio into frequency domain using FFT
2. **Peak Detection**: Identifies spectral peaks in different frequency ranges
3. **Constellation Mapping**: Creates unique fingerprints from frequency pairs
4. **Database Storage**: Stores fingerprints with time offsets in SQLite database
5. **Matching Algorithm**: Uses time alignment to find the best match

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install system dependencies**:
   
   **macOS**:
   ```bash
   # Install portaudio for pyaudio
   brew install portaudio
   
   # Install ffmpeg for audio format support
   brew install ffmpeg
   ```
   
   **Linux (Ubuntu/Debian)**:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pyaudio portaudio19-dev ffmpeg
   ```
   
   **Windows**:
   - Download and install ffmpeg from https://ffmpeg.org/
   - PyAudio wheels are available for Windows via pip

## Usage

### Interactive Mode

Run the main script to use the interactive interface:

```bash
python shazam.py
```

This will present you with options to:
1. Record and identify songs
2. Identify songs from audio files
3. Add songs to the database
4. List songs in database
5. Visualize audio spectrograms

### Programmatic Usage

```python
from shazam import Shazam

# Initialize the system
shazam = Shazam()

# Add a song to the database
shazam.add_song_to_database("path/to/song.wav", "Song Name", "Artist Name")

# Record and identify a song
result = shazam.record_and_identify(record_seconds=10)
if result:
    name, artist, confidence = result
    print(f"Identified: {name} by {artist}")

# Identify from file
result = shazam.identify_song("path/to/unknown_song.wav")

# Clean up
shazam.close()
```

### Testing

Run the test script to verify everything is working:

```bash
python test_shazam.py
```

## Project Structure

```
shazam/
├── shazam.py           # Main application code
├── test_shazam.py      # Test script
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Core Components

### AudioRecorder
- Records audio from microphone using PyAudio
- Supports configurable sample rates and recording duration
- Progress indicators during recording

### AudioAnalyzer
- Processes audio using FFT with Hamming windowing
- Detects spectral peaks in multiple frequency ranges
- Generates robust fingerprints using constellation mapping
- Supports multiple audio formats via librosa and pydub

### Database
- SQLite database for storing songs and fingerprints
- Optimized with indexes for fast lookups
- Batch processing for efficient fingerprint storage

### SongMatcher
- Advanced matching algorithm with time alignment
- Confidence scoring based on aligned matches
- Configurable minimum match thresholds

### Shazam (Main Class)
- Orchestrates all components
- Provides high-level API
- Interactive command-line interface

## Technical Details

### Fingerprinting Algorithm

1. **Windowing**: Apply Hamming window to reduce spectral leakage
2. **FFT**: Compute Fast Fourier Transform for frequency analysis
3. **Peak Detection**: Find local maxima above threshold in frequency ranges
4. **Constellation**: Create pairs of peaks with time differences
5. **Hashing**: Generate robust hashes using MD5 of quantized frequencies

### Matching Process

1. **Query Processing**: Generate fingerprints from unknown audio
2. **Database Search**: Find matching hashes in stored fingerprints
3. **Time Alignment**: Group matches by song and find consistent time offsets
4. **Scoring**: Count aligned matches to determine confidence
5. **Result**: Return best match above minimum threshold

## Performance Optimization

- **Batch Processing**: Insert fingerprints in batches for better database performance
- **Indexing**: Database indexes on hash and song_id for fast lookups
- **Quantization**: Frequency quantization reduces noise sensitivity
- **Windowing**: Hamming window improves frequency resolution

## Limitations

- **Database Size**: Performance degrades with very large song databases
- **Audio Quality**: Poor quality recordings may not match well
- **Similar Songs**: May confuse songs with similar spectral patterns
- **Background Noise**: High noise levels can affect recognition accuracy

## Troubleshooting

### Common Issues

1. **PyAudio Installation Errors**:
   - Ensure portaudio is installed on your system
   - Try: `pip install --upgrade pyaudio`

2. **Audio Format Errors**:
   - Install ffmpeg for audio conversion support
   - Check if the audio file is corrupted

3. **No Microphone Detected**:
   - Check microphone permissions
   - Verify microphone is connected and working

4. **Poor Recognition Results**:
   - Ensure good audio quality
   - Add more songs to the database
   - Try longer recording duration

### Performance Tips

- Use high-quality audio files when adding to database
- Record in quiet environments for better identification
- Regularly clean up the database of unused songs
- Use SSD storage for better database performance

## References

- [How Shazam Works](https://www.toptal.com/algorithms/shazam-it-music-processing-fingerprinting-and-recognition)
- [Audio Fingerprinting with Python](https://github.com/worldveil/dejavu)
- [Spectral Peak Detection](https://en.wikipedia.org/wiki/Peak_detection)


## Contributing

Feel free to submit issues and enhancement requests!
