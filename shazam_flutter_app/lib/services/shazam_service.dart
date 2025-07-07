import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/song.dart';

class ShazamService {
  // Use 10.0.2.2 for Android emulator to connect to host machine's localhost
  static const String baseUrl = 'http://10.0.2.2:8000';

  Future<RecognitionResult> identifySong(String audioFilePath) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/identify'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'file_path': audioFilePath}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success']) {
          return RecognitionResult.fromJson(data);
        }
      }

      return RecognitionResult.noMatch();
    } catch (e) {
      print('Error identifying song: $e');
      return RecognitionResult.noMatch();
    }
  }

  Future<List<Song>> getAllSongs() async {
    try {
      print('🔍 Fetching songs from: $baseUrl/songs');
      final response = await http
          .get(
            Uri.parse('$baseUrl/songs'),
            headers: {'Content-Type': 'application/json'},
          )
          .timeout(const Duration(seconds: 10));

      print('📡 Response status: ${response.statusCode}');
      print('📄 Response body: ${response.body}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success']) {
          final List<dynamic> songsJson = data['songs'];
          print('✅ Found ${songsJson.length} songs in response');
          return songsJson.map((songJson) => Song.fromJson(songJson)).toList();
        } else {
          print('❌ Server returned success: false');
        }
      } else {
        print('❌ HTTP error: ${response.statusCode}');
      }

      return [];
    } catch (e) {
      print('❌ Error getting songs: $e');
      return [];
    }
  }

  Future<bool> addSong(
    String audioFilePath,
    String name,
    String artist,
    String? album,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/add-song'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'file_path': audioFilePath,
          'name': name,
          'artist': artist,
          'album': album,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['success'] == true;
      }

      return false;
    } catch (e) {
      print('Error adding song: $e');
      return false;
    }
  }

  Future<RecognitionResult> recordAndIdentify(int durationSeconds) async {
    try {
      print('🎤 Recording and identifying for $durationSeconds seconds...');
      final response = await http
          .post(
            Uri.parse('$baseUrl/record-identify'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'duration': durationSeconds}),
          )
          .timeout(
            Duration(seconds: durationSeconds + 30),
          ); // Extra time for processing

      print('📡 Record response status: ${response.statusCode}');
      print('📄 Record response body: ${response.body}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success']) {
          return RecognitionResult.fromJson(data);
        }
      }

      return RecognitionResult.noMatch();
    } catch (e) {
      print('❌ Error recording and identifying: $e');
      return RecognitionResult.noMatch();
    }
  }

  Future<bool> isServerRunning() async {
    try {
      final response = await http
          .get(Uri.parse(baseUrl))
          .timeout(const Duration(seconds: 3));
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}
