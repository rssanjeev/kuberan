import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'tabs/enricher_tab.dart';
import 'tabs/stock_tracker_tab.dart';

/// Stocks page with tabs - Main hub for stock tracking and enrichment monitoring
/// 
/// FILE LOCATION: frontend/kuberan_app/lib/screens/stocks_tabs_screen.dart
/// 
/// PURPOSE: Container for stock-related features with two tabs:
/// - Enricher Tab: Enrichment progress, system status (former Home screen)
/// - Stock Tracker Tab: Stock list, search, pagination (former Stocks screen)
/// 
/// NAVIGATION:
/// - Route: '/' (default landing page)
/// - Accessible from: Side drawer
/// 
/// STATE MANAGEMENT:
/// - TabController manages tab switching
/// - Each tab handles its own data loading
class StocksTabsScreen extends StatefulWidget {
  const StocksTabsScreen({super.key});

  @override
  State<StocksTabsScreen> createState() => _StocksTabsScreenState();
}

class _StocksTabsScreenState extends State<StocksTabsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this); // Enricher + Stock Tracker
    
    // Check for tab query parameter and navigate to specific tab
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final uri = Uri.base;
      final tabParam = uri.queryParameters['tab'];
      if (tabParam != null) {
        final tabIndex = int.tryParse(tabParam);
        if (tabIndex != null && tabIndex >= 0 && tabIndex < 2) {
          _tabController.animateTo(tabIndex);
        }
      }
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

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
                child: const Icon(
                  Icons.account_balance,
                  size: 28,
                ),
              ),
            ],
          ),
        ),
        centerTitle: true,
        title: const Text(
          'Kuberan Stock Tracker',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        backgroundColor: const Color(0xFF3B82F6), // Budget App blue
        iconTheme: const IconThemeData(color: Colors.white),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          indicatorWeight: 3,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(
              icon: Icon(Icons.trending_up),
              text: 'Enricher',
            ),
            Tab(
              icon: Icon(Icons.list_alt),
              text: 'Stock Tracker',
            ),
          ],
        ),
      ),
      drawer: _buildDrawer(context),
      body: TabBarView(
        controller: _tabController,
        children: const [
          EnricherTab(),
          StockTrackerTab(),
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
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color(0xFF3B82F6), // Blue
                  Color(0xFF6366F1), // Indigo
                ],
              ),
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
                  Icon(Icons.account_balance_wallet, size: 48, color: Colors.white),
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
                    'Financial Management',
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
            initiallyExpanded: true,
            children: [
              ListTile(
                leading: const Icon(Icons.autorenew),
                title: const Text('  Enricher'),
                selected: _tabController.index == 0,
                onTap: () {
                  Navigator.pop(context);
                  _tabController.animateTo(0);
                },
              ),
              ListTile(
                leading: const Icon(Icons.trending_up),
                title: const Text('  Stock Tracker'),
                selected: _tabController.index == 1,
                onTap: () {
                  Navigator.pop(context);
                  _tabController.animateTo(1);
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
