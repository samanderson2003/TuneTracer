import numpy as np
import pyaudio
import wave
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to avoid warnings
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore', category=UserWarning)  # Suppress matplotlib warnings
warnings.filterwarnings('ignore', category=FutureWarning)  # Suppress future warnings
from scipy.fft import fft  # Use scipy.fft instead of deprecated scipy.fftpack
import sqlite3
import os
from collections import defaultdict
from datetime import datetime
import librosa
import librosa.display  # Explicitly import display module
from pydub import AudioSegment
from pydub.utils import which
import hashlib

class AudioRecorder:
    def __init__(self, chunk=4096, channels=1, rate=44100, record_seconds=10):
        self.CHUNK = chunk
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = channels
        self.RATE = rate
        self.RECORD_SECONDS = record_seconds
        
        # Initialize PyAudio with error suppression
        import logging
        logging.getLogger('pyaudio').setLevel(logging.ERROR)
        
        try:
            self.p = pyaudio.PyAudio()
        except Exception as e:
            print(f"Warning: PyAudio initialization issue: {e}")
            self.p = None
        
    def record(self, output_file="output.wav", record_seconds=None):
        if record_seconds is None:
            record_seconds = self.RECORD_SECONDS
            
        if self.p is None:
            print("Error: PyAudio not properly initialized")
            return None
            
        frames = []
        
        try:
            stream = self.p.open(format=self.FORMAT,
                                channels=self.CHANNELS,
                                rate=self.RATE,
                                input=True,
                                frames_per_buffer=self.CHUNK)
            
            print(f"* Recording for {record_seconds} seconds...")
            
            for i in range(0, int(self.RATE / self.CHUNK * record_seconds)):
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                frames.append(data)
                if i % 10 == 0:  # Progress indicator
                    progress = (i * self.CHUNK) / (self.RATE * record_seconds) * 100
                    print(f"Recording... {progress:.1f}%", end='\r')
            
            print("\n* Done recording")
            
            stream.stop_stream()
            stream.close()
            
            wf = wave.open(output_file, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            return output_file
            
        except Exception as e:
            print(f"Error during recording: {e}")
            return None
    
    def close(self):
        if self.p:
            self.p.terminate()

class AudioAnalyzer:
    def __init__(self, chunk_size=4096, rate=44100):
        self.CHUNK_SIZE = chunk_size
        self.RATE = rate
        # Improved frequency ranges for better fingerprinting
        self.RANGES = [40, 80, 120, 180, 300, 500, 1000, 2000]
        self.FUZ_FACTOR = 2
        
    def read_audio(self, filename):
        """Read audio file with support for multiple formats"""
        try:
            # Try reading as WAV first
            if filename.endswith('.wav'):
                wf = wave.open(filename, 'rb')
                frames = wf.readframes(wf.getnframes())
                audio = np.frombuffer(frames, dtype=np.int16)
                wf.close()
                return audio
            else:
                # Use librosa for other formats
                audio, sr = librosa.load(filename, sr=self.RATE, mono=True)
                return (audio * 32767).astype(np.int16)  # Convert to int16
        except Exception as e:
            print(f"Error reading audio file {filename}: {e}")
            return None
    
    def convert_audio_format(self, input_file, output_file=None):
        """Convert audio file to WAV format"""
        if output_file is None:
            output_file = os.path.splitext(input_file)[0] + '.wav'
        
        try:
            # Check if ffmpeg is available
            if which("ffmpeg") is None:
                print("Warning: ffmpeg not found. Audio conversion may fail for some formats.")
            
            audio = AudioSegment.from_file(input_file)
            audio = audio.set_frame_rate(self.RATE).set_channels(1)
            audio.export(output_file, format="wav")
            return output_file
        except Exception as e:
            print(f"Error converting audio format: {e}")
            print("Try installing ffmpeg: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)")
            return None
    
    def get_fft(self, data):
        """Compute FFT with windowing for better frequency resolution"""
        # Apply Hamming window to reduce spectral leakage
        windowed_data = data * np.hamming(len(data))
        fft_data = fft(windowed_data)
        # Handle both complex and real FFT results
        if np.iscomplexobj(fft_data):
            fft_data = np.abs(fft_data[0:len(fft_data)//2])
        else:
            fft_data = fft_data[0:len(fft_data)//2]
        return fft_data
    
    def get_index(self, freq):
        """Get frequency range index"""
        for i, range_freq in enumerate(self.RANGES):
            if freq < range_freq:
                return i
        return len(self.RANGES) - 1
    
    def find_peaks(self, fft_data, min_freq=40, max_freq=2000):
        """Find spectral peaks in the FFT data"""
        peaks = {}
        
        # Convert frequency to FFT bin
        freq_to_bin = lambda f: int(f * len(fft_data) * 2 / self.RATE)
        
        min_bin = freq_to_bin(min_freq)
        max_bin = min(freq_to_bin(max_freq), len(fft_data) - 1)
        
        # Find local maxima
        for i in range(min_bin + 1, max_bin - 1):
            if (fft_data[i] > fft_data[i-1] and 
                fft_data[i] > fft_data[i+1] and 
                fft_data[i] > np.mean(fft_data) * 2):  # Threshold
                
                freq = i * self.RATE / (2 * len(fft_data))
                range_idx = self.get_index(freq)
                
                if range_idx not in peaks or fft_data[i] > peaks[range_idx][1]:
                    peaks[range_idx] = (freq, fft_data[i])
        
        return peaks
    
    def generate_fingerprint(self, audio_data):
        """Generate audio fingerprints using constellation mapping"""
        num_chunks = len(audio_data) // self.CHUNK_SIZE
        fingerprints = []
        
        print(f"Generating fingerprints from {num_chunks} chunks...")
        
        for i in range(num_chunks):
            start = i * self.CHUNK_SIZE
            end = start + self.CHUNK_SIZE
            chunk = audio_data[start:end]
            
            if len(chunk) < self.CHUNK_SIZE:
                continue
                
            fft_data = self.get_fft(chunk)
            peaks = self.find_peaks(fft_data)
            
            if len(peaks) >= 2:
                # Create constellation pairs
                peak_freqs = sorted([freq for freq, mag in peaks.values()])
                
                # Generate hash pairs
                for j in range(len(peak_freqs) - 1):
                    freq1 = peak_freqs[j]
                    freq2 = peak_freqs[j + 1]
                    
                    # Create hash from frequency pair and time offset
                    h = self.hash_constellation(freq1, freq2, i)
                    time_offset = i * (self.CHUNK_SIZE / self.RATE)
                    fingerprints.append((h, time_offset))
            
            if i % 100 == 0:
                progress = i / num_chunks * 100
                print(f"Progress: {progress:.1f}%", end='\r')
        
        print(f"\nGenerated {len(fingerprints)} fingerprints")
        return fingerprints
    
    def hash_constellation(self, freq1, freq2, time_delta):
        """Create hash from constellation points"""
        # Quantize frequencies to reduce noise sensitivity
        freq1_q = int(freq1 / self.FUZ_FACTOR) * self.FUZ_FACTOR
        freq2_q = int(freq2 / self.FUZ_FACTOR) * self.FUZ_FACTOR
        
        # Create a more robust hash
        hash_string = f"{freq1_q}|{freq2_q}|{time_delta}"
        return int(hashlib.md5(hash_string.encode()).hexdigest()[:8], 16)

class Database:
    def __init__(self, db_file="songs.db"):
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        
    def connect(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        
    def close(self):
        if self.conn:
            self.conn.close()
            
    def initialize(self):
        """Initialize database with improved schema"""
        self.connect()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                artist TEXT NOT NULL,
                album TEXT,
                file_path TEXT NOT NULL,
                duration REAL,
                date_added TEXT NOT NULL,
                fingerprint_count INTEGER DEFAULT 0
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS fingerprints (
                hash INTEGER NOT NULL,
                song_id INTEGER NOT NULL,
                offset REAL NOT NULL,
                FOREIGN KEY (song_id) REFERENCES songs (id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for better performance
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_fingerprints_hash ON fingerprints (hash)
        ''')
        
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_fingerprints_song ON fingerprints (song_id)
        ''')
        
        self.conn.commit()
        
    def add_song(self, name, artist, file_path, fingerprints, album=None, duration=None):
        """Add song with improved metadata"""
        date_added = datetime.now().isoformat()
        
        self.cursor.execute('''
            INSERT INTO songs (name, artist, album, file_path, duration, date_added, fingerprint_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, artist, album, file_path, duration, date_added, len(fingerprints)))
        
        song_id = self.cursor.lastrowid
        
        # Add fingerprints in batches for better performance
        batch_size = 1000
        for i in range(0, len(fingerprints), batch_size):
            batch = fingerprints[i:i + batch_size]
            self.cursor.executemany('''
                INSERT INTO fingerprints (hash, song_id, offset)
                VALUES (?, ?, ?)
            ''', [(h, song_id, offset) for h, offset in batch])
        
        self.conn.commit()
        print(f"Added song '{name}' by {artist} with {len(fingerprints)} fingerprints")
        return song_id
    
    def find_matches(self, fingerprints):
        """Find matching fingerprints with improved querying"""
        if not fingerprints:
            return []
            
        hashes = [str(f[0]) for f in fingerprints]
        
        # Use parameterized query for safety
        placeholders = ','.join(['?'] * len(hashes))
        query = f'''
            SELECT f.hash, f.song_id, f.offset, s.name, s.artist
            FROM fingerprints f
            JOIN songs s ON f.song_id = s.id
            WHERE f.hash IN ({placeholders})
        '''
        
        self.cursor.execute(query, hashes)
        return self.cursor.fetchall()
    
    def get_song_info(self, song_id):
        """Get detailed song information"""
        self.cursor.execute('''
            SELECT name, artist, album, duration, date_added, fingerprint_count
            FROM songs WHERE id = ?
        ''', (song_id,))
        return self.cursor.fetchone()
    
    def get_all_songs(self):
        """Get list of all songs in database"""
        self.cursor.execute('''
            SELECT id, name, artist, album, fingerprint_count
            FROM songs ORDER BY name
        ''')
        return self.cursor.fetchall()
    
    def delete_song(self, song_id):
        """Delete a song and its fingerprints"""
        self.cursor.execute('DELETE FROM songs WHERE id = ?', (song_id,))
        self.conn.commit()

class SongMatcher:
    def __init__(self, database):
        self.db = database
        
    def match(self, query_fingerprints, min_matches=5):
        """Improved matching algorithm with time alignment"""
        matches = self.db.find_matches(query_fingerprints)
        
        if not matches:
            return None
        
        # Group matches by song and calculate time alignment
        song_matches = defaultdict(list)
        query_times = {h: t for h, t in query_fingerprints}
        
        for h, song_id, db_offset, name, artist in matches:
            if h in query_times:
                query_offset = query_times[h]
                time_diff = db_offset - query_offset
                song_matches[song_id].append((time_diff, name, artist))
        
        # Find best match using time alignment
        best_song = None
        best_score = 0
        
        for song_id, time_diffs in song_matches.items():
            if len(time_diffs) < min_matches:
                continue
                
            # Find the most common time difference (alignment)
            time_diff_counts = defaultdict(int)
            for time_diff, name, artist in time_diffs:
                # Quantize time differences to handle small variations
                quantized_diff = round(time_diff * 10) / 10
                time_diff_counts[quantized_diff] += 1
            
            if time_diff_counts:
                max_aligned_matches = max(time_diff_counts.values())
                if max_aligned_matches > best_score:
                    best_score = max_aligned_matches
                    best_song = (time_diffs[0][1], time_diffs[0][2], max_aligned_matches)
        
        return best_song

class Shazam:
    def __init__(self, db_file="songs.db"):
        self.recorder = AudioRecorder()
        self.analyzer = AudioAnalyzer()
        self.db = Database(db_file)
        self.db.initialize()
        self.matcher = SongMatcher(self.db)
        
    def record_and_identify(self, record_seconds=10):
        """Record audio and identify the song"""
        print("Starting recording...")
        audio_file = self.recorder.record("temp_recording.wav", record_seconds)
        
        if audio_file:
            print("Analyzing recorded audio...")
            return self.identify_song(audio_file)
        else:
            print("Recording failed")
            return None
    
    def identify_song(self, audio_file):
        """Identify a song from an audio file"""
        print(f"Identifying song from {audio_file}...")
        
        # Read and analyze audio
        audio_data = self.analyzer.read_audio(audio_file)
        if audio_data is None:
            return None
            
        fingerprints = self.analyzer.generate_fingerprint(audio_data)
        
        if not fingerprints:
            print("No fingerprints generated")
            return None
        
        # Match against database
        result = self.matcher.match(fingerprints)
        
        if result:
            name, artist, confidence = result
            print(f"Match found with confidence: {confidence}")
            return (name, artist, confidence)
        else:
            return None
    
    def add_song_to_database(self, audio_file, name, artist, album=None):
        """Add a song to the database"""
        print(f"Adding '{name}' by {artist} to database...")
        
        # Convert to WAV if necessary
        if not audio_file.endswith('.wav'):
            audio_file = self.analyzer.convert_audio_format(audio_file)
            if not audio_file:
                return None
        
        audio_data = self.analyzer.read_audio(audio_file)
        if audio_data is None:
            return None
            
        # Calculate duration
        duration = len(audio_data) / self.analyzer.RATE
        
        fingerprints = self.analyzer.generate_fingerprint(audio_data)
        
        if fingerprints:
            return self.db.add_song(name, artist, audio_file, fingerprints, album, duration)
        else:
            print("Failed to generate fingerprints")
            return None
    
    def list_songs(self):
        """List all songs in the database"""
        songs = self.db.get_all_songs()
        if songs:
            print("\nSongs in database:")
            print("-" * 60)
            for song_id, name, artist, album, fingerprint_count in songs:
                album_str = f" (Album: {album})" if album else ""
                print(f"{song_id}: {name} by {artist}{album_str} - {fingerprint_count} fingerprints")
        else:
            print("No songs in database")
    
    def visualize_spectrogram(self, audio_file):
        """Visualize the spectrogram of an audio file"""
        try:
            audio_data = self.analyzer.read_audio(audio_file)
            if audio_data is None:
                return
                
            # Switch to interactive backend for display
            matplotlib.use('TkAgg')
            
            plt.figure(figsize=(12, 6))
            
            # Convert to float for librosa
            audio_float = audio_data.astype(np.float32) / 32767.0
            
            # Generate spectrogram with proper parameters
            D = librosa.amplitude_to_db(
                np.abs(librosa.stft(audio_float, hop_length=512)), 
                ref=np.max
            )
            
            plt.subplot(2, 1, 1)
            librosa.display.specshow(
                D, 
                y_axis='hz', 
                x_axis='time', 
                sr=self.analyzer.RATE,
                hop_length=512
            )
            plt.colorbar(format='%+2.0f dB')
            plt.title('Spectrogram')
            
            # Plot waveform
            plt.subplot(2, 1, 2)
            time = np.arange(len(audio_data)) / self.analyzer.RATE
            plt.plot(time, audio_data)
            plt.title('Waveform')
            plt.xlabel('Time (s)')
            plt.ylabel('Amplitude')
            
            plt.tight_layout()
            plt.show()
            
            # Switch back to non-interactive backend
            matplotlib.use('Agg')
            
        except Exception as e:
            print(f"Visualization error: {e}")
            print("Matplotlib display may not be available in this environment")
    
    def close(self):
        """Clean up resources"""
        self.recorder.close()
        self.db.close()

def main():
    """Main interactive interface"""
    shazam = Shazam()
    
    print("🎵 Shazam-like Music Recognition System 🎵")
    print("==========================================")
    
    while True:
        print("\nOptions:")
        print("1. Record and identify song")
        print("2. Identify song from file")
        print("3. Add song to database")
        print("4. List songs in database")
        print("5. Visualize audio spectrogram")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        try:
            if choice == '1':
                seconds = input("Recording duration in seconds (default 10): ").strip()
                seconds = int(seconds) if seconds else 10
                
                result = shazam.record_and_identify(seconds)
                if result:
                    name, artist, confidence = result
                    print(f"\n🎉 Identified: '{name}' by {artist}")
                    print(f"Confidence: {confidence} matches")
                else:
                    print("\n❌ No matching song found")
            
            elif choice == '2':
                file_path = input("Enter audio file path: ").strip()
                if os.path.exists(file_path):
                    result = shazam.identify_song(file_path)
                    if result:
                        name, artist, confidence = result
                        print(f"\n🎉 Identified: '{name}' by {artist}")
                        print(f"Confidence: {confidence} matches")
                    else:
                        print("\n❌ No matching song found")
                else:
                    print("File not found")
            
            elif choice == '3':
                file_path = input("Enter audio file path: ").strip()
                if os.path.exists(file_path):
                    name = input("Song name: ").strip()
                    artist = input("Artist name: ").strip()
                    album = input("Album (optional): ").strip() or None
                    
                    song_id = shazam.add_song_to_database(file_path, name, artist, album)
                    if song_id:
                        print(f"\n✅ Successfully added song with ID: {song_id}")
                    else:
                        print("\n❌ Failed to add song")
                else:
                    print("File not found")
            
            elif choice == '4':
                shazam.list_songs()
            
            elif choice == '5':
                file_path = input("Enter audio file path: ").strip()
                if os.path.exists(file_path):
                    shazam.visualize_spectrogram(file_path)
                else:
                    print("File not found")
            
            elif choice == '6':
                print("Goodbye! 👋")
                break
            
            else:
                print("Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user")
        except Exception as e:
            print(f"\nError: {e}")
    
    shazam.close()

if __name__ == "__main__":
    main()
