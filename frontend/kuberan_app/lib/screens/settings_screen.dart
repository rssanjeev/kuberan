import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../widgets/theme_controller.dart';

/// Settings screen with dark mode toggle
class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final themeController = ThemeController.of(context);
    final brightness = MediaQuery.of(context).platformBrightness;
    
    // Check if we're in system mode or explicitly set
    final isSystemMode = themeController.themeMode == ThemeMode.system;
    final isDarkMode = themeController.themeMode == ThemeMode.dark || 
                       (isSystemMode && brightness == Brightness.dark);

    return Scaffold(
      appBar: AppBar(
        leadingWidth: 100,
        leading: Builder(
          builder: (context) => Row(
            children: [
              IconButton(
                icon: const Icon(Icons.menu),
                onPressed: () => Scaffold.of(context).openDrawer(),
                tooltip: 'Open navigation menu',
              ),
              GestureDetector(
                onTap: () => context.go('/'),
                child: const Icon(Icons.account_balance, size: 28),
              ),
            ],
          ),
        ),
        automaticallyImplyLeading: false,
        title: const Text('Settings'),
        centerTitle: true,
      ),
      drawer: _buildDrawer(context),
      body: ListView(
        children: [
          const SizedBox(height: 8),
          SwitchListTile(
            secondary: const Icon(Icons.brightness_6),
            title: const Text('Dark Mode'),
            subtitle: const Text('Enable dark theme'),
            value: isDarkMode,
            onChanged: (bool value) {
              themeController.toggleTheme(value);
            },
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.info_outline),
            title: const Text('About'),
            subtitle: const Text('App version and information'),
            onTap: () {
              showAboutDialog(
                context: context,
                applicationName: 'Kuberan',
                applicationVersion: '1.0.0',
                applicationIcon: const Icon(Icons.account_balance, size: 48),
                children: const [
                  Text('Your financial companion for smart money management.'),
                ],
              );
            },
          ),
        ],
      ),
    );
  }

  /// Build navigation drawer
  Widget _buildDrawer(BuildContext context) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          DrawerHeader(
            decoration: const BoxDecoration(
              color: Color(0xFF6366F1), // Purple for Settings
            ),
            child: InkWell(
              onTap: () {
                Navigator.pop(context);
                context.go('/');
              },
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  Icon(Icons.settings, size: 48, color: Colors.white),
                  SizedBox(height: 8),
                  Text(
                    'Kuberan',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    'Settings',
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
          ),
          ListTile(
            leading: const Icon(Icons.home),
            title: const Text('Home'),
            onTap: () {
              Navigator.pop(context);
              context.go('/');
            },
          ),
          ExpansionTile(
            leading: const Icon(Icons.show_chart),
            title: const Text('Stocks'),
            children: [
              ListTile(
                leading: const Icon(Icons.autorenew),
                title: const Text('  Enricher'),
                onTap: () {
                  Navigator.pop(context);
                  context.go('/stocks?tab=0');
                },
              ),
              ListTile(
                leading: const Icon(Icons.analytics),
                title: const Text('  Stock Tracker'),
                onTap: () {
                  Navigator.pop(context);
                  context.go('/stocks?tab=1');
                },
              ),
            ],
          ),
          ExpansionTile(
            leading: const Icon(Icons.account_balance_wallet),
            title: const Text('Financier'),
            children: [
              ListTile(
                leading: const Icon(Icons.receipt_long),
                title: const Text('  Expense Tracker'),
                onTap: () {
                  Navigator.pop(context);
                  context.go('/financier?tab=0');
                },
              ),
              ListTile(
                leading: const Icon(Icons.trending_up),
                title: const Text('  Investment Analysis'),
                onTap: () {
                  Navigator.pop(context);
                  context.go('/financier?tab=1');
                },
              ),
            ],
          ),
          ListTile(
            leading: const Icon(Icons.settings),
            title: const Text('Settings'),
            selected: true,
            onTap: () {
              Navigator.pop(context);
              // Already on settings page
            },
          ),
        ],
      ),
    );
  }
}
