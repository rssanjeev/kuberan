import 'package:flutter/material.dart';
import 'routes/app_router.dart';
import 'widgets/theme_controller.dart';

void main() {
  runApp(const KuberanApp());
}

class KuberanApp extends StatefulWidget {
  const KuberanApp({super.key});

  @override
  State<KuberanApp> createState() => _KuberanAppState();
}

class _KuberanAppState extends State<KuberanApp> {
  ThemeMode _themeMode = ThemeMode.system;

  void _toggleTheme(bool isDark) {
    setState(() {
      _themeMode = isDark ? ThemeMode.dark : ThemeMode.light;
    });
  }

  @override
  Widget build(BuildContext context) {
    return ThemeController(
      themeMode: _themeMode,
      toggleTheme: _toggleTheme,
      child: MaterialApp.router(
        title: 'Kuberan Stock Tracker',
        debugShowCheckedModeBanner: false,
        routerConfig: appRouter,
        themeMode: _themeMode,
        theme: ThemeData(
          // Budget App color scheme - Light theme
          primaryColor: const Color(0xFF3B82F6), // Blue
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF3B82F6),
            secondary: const Color(0xFF6366F1), // Indigo
            brightness: Brightness.light,
          ),
          scaffoldBackgroundColor: Colors.white,
          cardTheme: CardThemeData(
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: BorderSide(color: Colors.grey.shade300, width: 1),
            ),
          ),
          appBarTheme: const AppBarTheme(
            backgroundColor: Color(0xFF3B82F6),
            foregroundColor: Colors.white,
            elevation: 0,
          ),
          useMaterial3: true,
        ),
        darkTheme: ThemeData(
          // Dark theme
          primaryColor: const Color(0xFF3B82F6), // Keep brand blue
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF3B82F6),
            secondary: const Color(0xFF6366F1), // Indigo
            brightness: Brightness.dark,
          ),
          scaffoldBackgroundColor: const Color(0xFF121212),
          cardTheme: CardThemeData(
            elevation: 4,
            color: const Color(0xFF1E1E1E),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: BorderSide(color: Colors.grey.shade800, width: 1),
            ),
          ),
          appBarTheme: const AppBarTheme(
            backgroundColor: Color(0xFF1E1E1E),
            foregroundColor: Colors.white,
            elevation: 0,
          ),
          useMaterial3: true,
        ),
      ),
    );
  }
}
