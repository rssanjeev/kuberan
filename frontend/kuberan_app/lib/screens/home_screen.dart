import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leadingWidth: 100,
        leading: Builder(
          builder: (context) => Row(
            children: [
              IconButton(
                icon: const Icon(Icons.menu),
                onPressed: () => Scaffold.of(context).openDrawer(),
              ),
              GestureDetector(
                onTap: () => context.go('/'),
                child: const Icon(Icons.account_balance, size: 28),
              ),
            ],
          ),
        ),
        title: const Text('Kuberan'),
        centerTitle: true,
      ),
      drawer: _buildDrawer(context),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 40),
              const Text(
                'Kuberan',
                style: TextStyle(
                  fontSize: 48,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF3B82F6),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Your Intelligent Stock & Financial Companion',
                style: TextStyle(
                  fontSize: 20,
                  color: Colors.grey[600],
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 40),
              
              // About section (placeholder)
              Card(
                elevation: 4,
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'About Kuberan',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Content will be updated in the future.\n\n'
                        'Kuberan is a comprehensive platform for stock tracking, '
                        'enrichment, and financial management. Track your investments, '
                        'analyze spending patterns, and make informed financial decisions.',
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.grey[700],
                          height: 1.5,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 32),
              
              // Navigation cards
              LayoutBuilder(
                builder: (context, constraints) {
                  if (constraints.maxWidth > 600) {
                    return Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        _buildNavigationCard(
                          context,
                          'Stocks',
                          'Track and analyze stock data with real-time enrichment',
                          Icons.show_chart,
                          '/stocks',
                        ),
                        const SizedBox(width: 16),
                        _buildNavigationCard(
                          context,
                          'Financier',
                          'Manage expenses and analyze investment patterns',
                          Icons.account_balance_wallet,
                          '/financier',
                        ),
                      ],
                    );
                  } else {
                    return Column(
                      children: [
                        _buildNavigationCard(
                          context,
                          'Stocks',
                          'Track and analyze stock data with real-time enrichment',
                          Icons.show_chart,
                          '/stocks',
                        ),
                        const SizedBox(height: 16),
                        _buildNavigationCard(
                          context,
                          'Financier',
                          'Manage expenses and analyze investment patterns',
                          Icons.account_balance_wallet,
                          '/financier',
                        ),
                      ],
                    );
                  }
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNavigationCard(
    BuildContext context,
    String title,
    String description,
    IconData icon,
    String route,
  ) {
    return SizedBox(
      width: 280,
      child: Card(
        elevation: 4,
        child: InkWell(
          onTap: () => context.go(route),
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              children: [
                Icon(icon, size: 48, color: const Color(0xFF3B82F6)),
                const SizedBox(height: 16),
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  description,
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Colors.grey[600],
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildDrawer(BuildContext context) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          DrawerHeader(
            decoration: const BoxDecoration(
              color: Color(0xFF3B82F6),
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
                  Icon(Icons.account_balance, size: 48, color: Colors.white),
                  SizedBox(height: 8),
                  Text(
                    'Kuberan',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: 4),
                  Text(
                    'Financial Companion',
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
            ),
          ),
          ListTile(
            leading: const Icon(Icons.home),
            title: const Text('Home'),
            selected: true,
            onTap: () => Navigator.pop(context),
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
                leading: const Icon(Icons.trending_up),
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
                leading: const Icon(Icons.assessment),
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
          const Divider(),
          ListTile(
            leading: const Icon(Icons.settings),
            title: const Text('Settings'),
            onTap: () {
              Navigator.pop(context);
              context.go('/settings');
            },
          ),
        ],
      ),
    );
  }
}
