import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/shazam_provider.dart';
import '../widgets/recording_widgets.dart';
import 'songs_screen.dart';
import 'add_song_screen.dart';
import 'identify_file_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  late PageController _pageController;

  @override
  void initState() {
    super.initState();
    _pageController = PageController();

    // Load songs when the app starts
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ShazamProvider>().loadSongs();
    });
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: PageView(
        controller: _pageController,
        onPageChanged: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        children: [
          const _RecognizeTab(),
          const SongsScreen(),
          const AddSongScreen(),
          const IdentifyFileScreen(),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _currentIndex,
        onTap: (index) {
          _pageController.animateToPage(
            index,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeInOut,
          );
        },
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.mic), label: 'Recognize'),
          BottomNavigationBarItem(
            icon: Icon(Icons.library_music),
            label: 'Songs',
          ),
          BottomNavigationBarItem(icon: Icon(Icons.add), label: 'Add Song'),
          BottomNavigationBarItem(
            icon: Icon(Icons.file_upload),
            label: 'From File',
          ),
        ],
      ),
    );
  }
}

class _RecognizeTab extends StatelessWidget {
  const _RecognizeTab();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('🎵 Shazam Flutter'),
        actions: [
          Consumer<ShazamProvider>(
            builder: (context, provider, child) {
              return PopupMenuButton<int>(
                icon: const Icon(Icons.timer),
                onSelected: (duration) {
                  provider.setRecordingDuration(duration);
                },
                itemBuilder: (context) => [
                  const PopupMenuItem(value: 5, child: Text('5 seconds')),
                  const PopupMenuItem(value: 10, child: Text('10 seconds')),
                  const PopupMenuItem(value: 15, child: Text('15 seconds')),
                  const PopupMenuItem(value: 30, child: Text('30 seconds')),
                ],
              );
            },
          ),
        ],
      ),
      body: Consumer<ShazamProvider>(
        builder: (context, provider, child) {
          return Stack(
            children: [
              SingleChildScrollView(
                child: Column(
                  children: [
                    const SizedBox(height: 40),

                    // Header
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 32),
                      child: Column(
                        children: [
                          Text(
                            'Discover Music',
                            style: Theme.of(context).textTheme.headlineMedium
                                ?.copyWith(fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Tap the button and let the magic happen',
                            style: Theme.of(context).textTheme.bodyLarge
                                ?.copyWith(color: Colors.grey.shade600),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 12),
                          // Connection Status
                          Consumer<ShazamProvider>(
                            builder: (context, provider, child) {
                              return Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 12,
                                  vertical: 6,
                                ),
                                decoration: BoxDecoration(
                                  color: provider.isServerConnected
                                      ? Colors.green.withOpacity(0.1)
                                      : Colors.red.withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(20),
                                  border: Border.all(
                                    color: provider.isServerConnected
                                        ? Colors.green
                                        : Colors.red,
                                    width: 1,
                                  ),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(
                                      provider.isServerConnected
                                          ? Icons.wifi
                                          : Icons.wifi_off,
                                      size: 16,
                                      color: provider.isServerConnected
                                          ? Colors.green
                                          : Colors.red,
                                    ),
                                    const SizedBox(width: 6),
                                    Text(
                                      provider.isServerConnected
                                          ? 'Server Connected'
                                          : 'Server Disconnected',
                                      style: TextStyle(
                                        color: provider.isServerConnected
                                            ? Colors.green
                                            : Colors.red,
                                        fontSize: 12,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                  ],
                                ),
                              );
                            },
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 60),

                    // Record Button
                    const RecordButton(),

                    const SizedBox(height: 20),

                    // Recording Duration Info
                    Consumer<ShazamProvider>(
                      builder: (context, provider, child) {
                        return Text(
                          'Recording duration: ${provider.recordingDuration}s',
                          style: Theme.of(context).textTheme.bodyMedium
                              ?.copyWith(color: Colors.grey.shade600),
                        );
                      },
                    ),

                    // Recording Progress
                    const RecordingProgress(),

                    const SizedBox(height: 20),

                    // State Message
                    if (provider.state == ShazamState.identifying)
                      Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          children: [
                            const CircularProgressIndicator(),
                            const SizedBox(height: 16),
                            Text(
                              'Identifying song...',
                              style: Theme.of(context).textTheme.titleMedium,
                            ),
                            Text(
                              'This may take a few moments',
                              style: Theme.of(context).textTheme.bodyMedium
                                  ?.copyWith(color: Colors.grey.shade600),
                            ),
                          ],
                        ),
                      ),

                    // Error Message
                    if (provider.state == ShazamState.error)
                      Padding(
                        padding: const EdgeInsets.all(16),
                        child: Card(
                          color: Colors.red.shade50,
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              children: [
                                Icon(
                                  Icons.error_outline,
                                  color: Colors.red.shade700,
                                  size: 32,
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  'Error',
                                  style: TextStyle(
                                    color: Colors.red.shade700,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 16,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  provider.errorMessage ?? 'Unknown error',
                                  style: TextStyle(color: Colors.red.shade600),
                                  textAlign: TextAlign.center,
                                ),
                                const SizedBox(height: 12),
                                ElevatedButton(
                                  onPressed: provider.clearError,
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.red.shade700,
                                  ),
                                  child: const Text(
                                    'Dismiss',
                                    style: TextStyle(color: Colors.white),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),

                    // Result Card
                    const ResultCard(),

                    const SizedBox(height: 40),

                    // Info Cards
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Row(
                        children: [
                          Expanded(
                            child: _InfoCard(
                              icon: Icons.library_music,
                              title: 'Songs in Database',
                              value: '${provider.songs.length}',
                              color: Theme.of(context).primaryColor,
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: _InfoCard(
                              icon: Icons.fingerprint,
                              title: 'Total Fingerprints',
                              value: provider.songs
                                  .fold(
                                    0,
                                    (sum, song) => sum + song.fingerprintCount,
                                  )
                                  .toString(),
                              color: Colors.orange,
                            ),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 40),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String value;
  final Color color;

  const _InfoCard({
    required this.icon,
    required this.title,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, size: 32, color: color),
            const SizedBox(height: 8),
            Text(
              value,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: Theme.of(
                context,
              ).textTheme.bodySmall?.copyWith(color: Colors.grey.shade600),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
