class Song {
  final int id;
  final String name;
  final String artist;
  final String? album;
  final String filePath;
  final double? duration;
  final DateTime dateAdded;
  final int fingerprintCount;

  Song({
    required this.id,
    required this.name,
    required this.artist,
    this.album,
    required this.filePath,
    this.duration,
    required this.dateAdded,
    required this.fingerprintCount,
  });

  factory Song.fromJson(Map<String, dynamic> json) {
    return Song(
      id: json['id'],
      name: json['name'],
      artist: json['artist'],
      album: json['album'],
      filePath: json['file_path'],
      duration: json['duration']?.toDouble(),
      dateAdded: DateTime.parse(json['date_added']),
      fingerprintCount: json['fingerprint_count'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'artist': artist,
      'album': album,
      'file_path': filePath,
      'duration': duration,
      'date_added': dateAdded.toIso8601String(),
      'fingerprint_count': fingerprintCount,
    };
  }

  String get durationFormatted {
    if (duration == null) return 'Unknown';
    final minutes = (duration! / 60).floor();
    final seconds = (duration! % 60).floor();
    return '${minutes}:${seconds.toString().padLeft(2, '0')}';
  }
}

class RecognitionResult {
  final String name;
  final String artist;
  final int confidence;
  final bool isMatch;

  RecognitionResult({
    required this.name,
    required this.artist,
    required this.confidence,
    required this.isMatch,
  });

  factory RecognitionResult.fromJson(Map<String, dynamic> json) {
    return RecognitionResult(
      name: json['name'] ?? 'Unknown',
      artist: json['artist'] ?? 'Unknown',
      confidence: json['confidence'] ?? 0,
      isMatch: json['is_match'] ?? false,
    );
  }

  factory RecognitionResult.noMatch() {
    return RecognitionResult(
      name: 'No Match',
      artist: 'Unknown',
      confidence: 0,
      isMatch: false,
    );
  }
}
