import 'package:flutter/material.dart';

/// InheritedWidget for managing app theme across the widget tree
class ThemeController extends InheritedWidget {
  final ThemeMode themeMode;
  final Function(bool isDark) toggleTheme;

  const ThemeController({
    super.key,
    required this.themeMode,
    required this.toggleTheme,
    required super.child,
  });

  /// Access ThemeController from anywhere in the widget tree
  static ThemeController of(BuildContext context) {
    final ThemeController? result = context.dependOnInheritedWidgetOfExactType<ThemeController>();
    assert(result != null, 'No ThemeController found in context');
    return result!;
  }

  @override
  bool updateShouldNotify(ThemeController old) => old.themeMode != themeMode;
}
