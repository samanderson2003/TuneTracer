import 'package:flutter/foundation.dart';
import '../models/song.dart';
import '../services/shazam_service.dart';

enum ShazamState { idle, recording, processing, identifying, loading, error }

class ShazamProvider extends ChangeNotifier {
  final ShazamService _service = ShazamService();

  ShazamState _state = ShazamState.idle;
  List<Song> _songs = [];
  RecognitionResult? _lastResult;
  String? _errorMessage;
  bool _isRecording = false;
  int _recordingDuration = 10;
  bool _isServerConnected = false;

  // Getters
  ShazamState get state => _state;
  List<Song> get songs => _songs;
  RecognitionResult? get lastResult => _lastResult;
  String? get errorMessage => _errorMessage;
  bool get isRecording => _isRecording;
  int get recordingDuration => _recordingDuration;
  bool get isServerConnected => _isServerConnected;
  bool get isLoading =>
      _state == ShazamState.loading ||
      _state == ShazamState.processing ||
      _state == ShazamState.identifying ||
      _state == ShazamState.recording;

  void _setState(ShazamState newState) {
    _state = newState;
    notifyListeners();
  }

  void _setError(String message) {
    _errorMessage = message;
    _setState(ShazamState.error);
  }

  void clearError() {
    _errorMessage = null;
    _setState(ShazamState.idle);
  }

  void setRecordingDuration(int duration) {
    _recordingDuration = duration;
    notifyListeners();
  }

  Future<void> loadSongs() async {
    _setState(ShazamState.loading);
    try {
      // First check server connection
      _isServerConnected = await _service.isServerRunning();
      print('🔗 Server connected: $_isServerConnected');

      if (!_isServerConnected) {
        _setError(
          'Cannot connect to Shazam server. Make sure the Python server is running on port 8000.',
        );
        return;
      }

      _songs = await _service.getAllSongs();
      print('📊 Loaded ${_songs.length} songs');
      _setState(ShazamState.idle);
    } catch (e) {
      print('❌ Error loading songs: $e');
      _setError('Failed to load songs: $e');
    }
  }

  Future<void> recordAndIdentify() async {
    _setState(ShazamState.recording);
    _isRecording = true;
    notifyListeners();

    try {
      // Simulate recording progress
      await Future.delayed(Duration(seconds: _recordingDuration));
      _isRecording = false;

      _setState(ShazamState.identifying);
      _lastResult = await _service.recordAndIdentify(_recordingDuration);

      _setState(ShazamState.idle);
    } catch (e) {
      _isRecording = false;
      _setError('Failed to record and identify: $e');
    }
  }

  Future<void> identifyFromFile(String filePath) async {
    _setState(ShazamState.processing);
    try {
      _lastResult = await _service.identifySong(filePath);
      _setState(ShazamState.idle);
    } catch (e) {
      _setError('Failed to identify song from file: $e');
    }
  }

  Future<bool> addSong(
    String filePath,
    String name,
    String artist,
    String? album,
  ) async {
    _setState(ShazamState.processing);
    try {
      final success = await _service.addSong(filePath, name, artist, album);
      if (success) {
        await loadSongs(); // Reload songs list
        _setState(ShazamState.idle);
        return true;
      } else {
        _setError('Failed to add song to database');
        return false;
      }
    } catch (e) {
      _setError('Failed to add song: $e');
      return false;
    }
  }

  void stopRecording() {
    _isRecording = false;
    _setState(ShazamState.idle);
  }

  void clearLastResult() {
    _lastResult = null;
    notifyListeners();
  }

  Future<void> testConnection() async {
    try {
      print('🔍 Testing server connection...');
      _isServerConnected = await _service.isServerRunning();
      print('🔗 Connection test result: $_isServerConnected');
      notifyListeners();
    } catch (e) {
      print('❌ Connection test failed: $e');
      _isServerConnected = false;
      notifyListeners();
    }
  }
}
