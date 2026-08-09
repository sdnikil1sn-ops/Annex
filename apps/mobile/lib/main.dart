import 'package:flutter/material.dart';

/// Entry point of the ANNEX mobile application.
void main() {
  runApp(const AnnexApp());
}

/// Root widget of the ANNEX mobile application.
///
/// Phase 1 ships a minimal, real shell. Navigation, state management
/// (MVVM/Clean Architecture), and feature modules arrive in Phase 8+.
class AnnexApp extends StatelessWidget {
  const AnnexApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ANNEX',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1B5E8A)),
        useMaterial3: true,
      ),
      home: const HomeShell(),
    );
  }
}

/// Temporary home screen for the ANNEX application shell.
class HomeShell extends StatelessWidget {
  const HomeShell({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ANNEX')),
      body: const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.auto_awesome, size: 64),
            SizedBox(height: 16),
            Text(
              'Learn Before You Believe',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }
}
