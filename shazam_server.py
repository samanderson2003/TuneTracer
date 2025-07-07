#!/usr/bin/env python3
"""
Simple HTTP server for Shazam Flutter app
Provides REST API endpoints for music recognition
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import os
import sys
import threading
import time

# Add the parent directory to path so we can import shazam
sys.path.append('/Users/samandersony/StudioProjects/projects/shazam')

try:
    from shazam import Shazam
    print("✅ Shazam module imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Shazam module: {e}")
    sys.exit(1)

class ShazamHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.shazam = Shazam()
        super().__init__(*args, **kwargs)
    
    def _set_cors_headers(self):
        """Set CORS headers for cross-origin requests"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def _send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error_response(self, message, status_code=500):
        """Send error response"""
        self._send_json_response({
            'success': False,
            'error': message
        }, status_code)
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path == '/':
                self._send_json_response({
                    'message': 'Shazam API Server',
                    'version': '1.0.0',
                    'endpoints': [
                        'GET /songs - List all songs',
                        'POST /identify - Identify song from file',
                        'POST /add-song - Add song to database',
                        'POST /record-identify - Record and identify'
                    ]
                })
            elif self.path == '/songs':
                self._handle_get_songs()
            else:
                self._send_error_response('Endpoint not found', 404)
        except Exception as e:
            print(f"Error in GET {self.path}: {e}")
            self._send_error_response(str(e))
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            if self.path == '/identify':
                self._handle_identify_song(data)
            elif self.path == '/add-song':
                self._handle_add_song(data)
            elif self.path == '/record-identify':
                self._handle_record_identify(data)
            else:
                self._send_error_response('Endpoint not found', 404)
        except Exception as e:
            print(f"Error in POST {self.path}: {e}")
            self._send_error_response(str(e))
    
    def _handle_get_songs(self):
        """Get all songs in database"""
        try:
            songs = self.shazam.db.get_all_songs()
            song_list = []
            
            for song in songs:
                song_id, name, artist, album, fingerprint_count = song
                song_info = self.shazam.db.get_song_info(song_id)
                if song_info:
                    name, artist, album, duration, date_added, fingerprint_count = song_info
                    song_list.append({
                        'id': song_id,
                        'name': name,
                        'artist': artist,
                        'album': album,
                        'file_path': '',
                        'duration': duration,
                        'date_added': date_added,
                        'fingerprint_count': fingerprint_count
                    })
            
            self._send_json_response({
                'success': True,
                'songs': song_list
            })
        except Exception as e:
            self._send_error_response(f"Failed to get songs: {e}")
    
    def _handle_identify_song(self, data):
        """Identify song from file path"""
        try:
            file_path = data.get('file_path')
            if not file_path:
                self._send_error_response('file_path is required', 400)
                return
            
            if not os.path.exists(file_path):
                self._send_error_response('File not found', 404)
                return
            
            print(f"🔍 Identifying song from: {file_path}")
            result = self.shazam.identify_song(file_path)
            
            if result:
                name, artist, confidence = result
                self._send_json_response({
                    'success': True,
                    'name': name,
                    'artist': artist,
                    'confidence': confidence,
                    'is_match': True
                })
            else:
                self._send_json_response({
                    'success': True,
                    'name': 'No Match',
                    'artist': 'Unknown',
                    'confidence': 0,
                    'is_match': False
                })
        except Exception as e:
            self._send_error_response(f"Failed to identify song: {e}")
    
    def _handle_add_song(self, data):
        """Add song to database"""
        try:
            file_path = data.get('file_path')
            name = data.get('name')
            artist = data.get('artist')
            album = data.get('album')
            
            if not all([file_path, name, artist]):
                self._send_error_response('file_path, name, and artist are required', 400)
                return
            
            if not os.path.exists(file_path):
                self._send_error_response('File not found', 404)
                return
            
            print(f"📚 Adding song to database: {name} by {artist}")
            song_id = self.shazam.add_song_to_database(file_path, name, artist, album)
            
            if song_id:
                self._send_json_response({
                    'success': True,
                    'song_id': song_id,
                    'message': f'Successfully added "{name}" by {artist}'
                })
            else:
                self._send_error_response('Failed to add song to database')
        except Exception as e:
            self._send_error_response(f"Failed to add song: {e}")
    
    def _handle_record_identify(self, data):
        """Record audio and identify"""
        try:
            duration = data.get('duration', 10)
            
            print(f"🎤 Recording for {duration} seconds...")
            result = self.shazam.record_and_identify(duration)
            
            if result:
                name, artist, confidence = result
                self._send_json_response({
                    'success': True,
                    'name': name,
                    'artist': artist,
                    'confidence': confidence,
                    'is_match': True
                })
            else:
                self._send_json_response({
                    'success': True,
                    'name': 'No Match',
                    'artist': 'Unknown',
                    'confidence': 0,
                    'is_match': False
                })
        except Exception as e:
            self._send_error_response(f"Failed to record and identify: {e}")
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        print(f"🌐 {self.address_string()} - {format % args}")

def run_server(port=8000):
    """Run the HTTP server"""
    # Bind to all interfaces so Android emulator can connect
    server_address = ('0.0.0.0', port)
    
    # Create a custom handler class that includes the Shazam instance
    class CustomShazamHandler(ShazamHandler):
        def __init__(self, *args, **kwargs):
            # Initialize Shazam instance once for the server
            if not hasattr(CustomShazamHandler, 'shazam_instance'):
                print("🔧 Initializing Shazam instance...")
                CustomShazamHandler.shazam_instance = Shazam()
                print("✅ Shazam instance ready")
            
            self.shazam = CustomShazamHandler.shazam_instance
            BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
    
    httpd = HTTPServer(server_address, CustomShazamHandler)
    
    print(f"🎵 Shazam API Server starting on port {port}")
    print(f"🌐 Server URL: http://localhost:{port}")
    print("📋 Available endpoints:")
    print("   GET  /           - Server info")
    print("   GET  /songs      - List all songs")
    print("   POST /identify   - Identify song from file")
    print("   POST /add-song   - Add song to database")
    print("   POST /record-identify - Record and identify")
    print("\n🚀 Server is ready! Press Ctrl+C to stop.\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        httpd.server_close()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Shazam API Server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run server on (default: 8000)')
    args = parser.parse_args()
    
    run_server(args.port)
