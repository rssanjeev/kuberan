import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'tabs/expense_tracker_tab.dart';
import 'tabs/investment_analysis_tab.dart';

/// Financier - Financial management and analytics hub
/// 
/// FILE LOCATION: frontend/kuberan_app/lib/screens/financier_screen.dart
/// 
/// PURPOSE: Main container for all financial management features with tabs:
/// - Expense Tracker: Cash flow analysis and spending breakdown
/// - [Future tabs]: Budgets, Investments, Reports, etc.
/// 
/// ARCHITECTURE:
/// - Uses TabController for tab navigation
/// - Manages global filters (year/month) that apply to all tabs
/// - Each tab is a separate widget in screens/tabs/ directory
/// 
/// STATE MANAGEMENT:
/// - selectedYear and selectedMonth passed to child tabs
/// - Tabs refresh when filters change
/// - onRefresh callback allows tabs to trigger parent refresh
class FinancierScreen extends StatefulWidget {
  const FinancierScreen({super.key});

  @override
  State<FinancierScreen> createState() => _FinancierScreenState();
}

class _FinancierScreenState extends State<FinancierScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  int? _selectedYear;
  int? _selectedMonth;
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this); // Expense Tracker + Investment Analysis
    
    // Default to previous month
    final now = DateTime.now();
    final previousMonth = DateTime(now.year, now.month - 1);
    _selectedYear = previousMonth.year;
    _selectedMonth = previousMonth.month;
    
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
  
  void _refreshCurrentTab() {
    setState(() {
      // Trigger rebuild to refresh current tab
    });
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
                child: const Icon(Icons.account_balance, size: 28),
              ),
            ],
          ),
        ),
        automaticallyImplyLeading: false,
        title: const Text('Financier'),
        centerTitle: true,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          indicatorWeight: 3,
          tabs: const [
            Tab(
              icon: Icon(Icons.assessment),
              text: 'Expense Tracker',
            ),
            Tab(
              icon: Icon(Icons.trending_up),
              text: 'Investment Analysis',
            ),
            // Future tabs:
            // Tab(icon: Icon(Icons.account_balance), text: 'Budgets'),
          ],
        ),
      ),
      drawer: _buildDrawer(context),
      body: Column(
        children: [
          // Global filter section (applies to all tabs)
          _buildFilterSection(),
          const SizedBox(height: 8),
          
          // Tab content
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                // Expense Tracker Tab
                ExpenseTrackerTab(
                  selectedYear: _selectedYear,
                  selectedMonth: _selectedMonth,
                  onRefresh: _refreshCurrentTab,
                ),
                // Investment Analysis Tab
                InvestmentAnalysisTab(
                  selectedYear: _selectedYear,
                  selectedMonth: _selectedMonth,
                  onRefresh: _refreshCurrentTab,
                ),
                // Future tabs will be added here
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterSection() {
    final currentYear = DateTime.now().year;
    final years = List.generate(3, (i) => currentYear - i);
    final months = [
      null, // "All Months" option
      1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
    ];
    
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: isDarkMode ? Colors.grey[850] : Colors.grey[100],
        border: Border(
          bottom: BorderSide(
            color: isDarkMode ? Colors.grey[700]! : Colors.grey[300]!, 
            width: 1
          ),
        ),
      ),
      child: Row(
        children: [
          const Text(
            'Filter: ',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              decoration: BoxDecoration(
                color: isDarkMode ? Colors.grey[800] : Colors.white,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: isDarkMode ? Colors.grey[600]! : Colors.grey[300]!
                ),
              ),
              child: DropdownButton<int?>(
                value: _selectedYear,
                hint: const Text('All Years'),
                isExpanded: true,
                underline: const SizedBox(),
                items: [
                  const DropdownMenuItem(value: null, child: Text('All Years')),
                  ...years.map((year) => DropdownMenuItem(
                    value: year,
                    child: Text(year.toString()),
                  )),
                ],
                onChanged: (value) {
                  setState(() {
                    _selectedYear = value;
                  });
                },
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              decoration: BoxDecoration(
                color: isDarkMode ? Colors.grey[800] : Colors.white,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: isDarkMode ? Colors.grey[600]! : Colors.grey[300]!
                ),
              ),
              child: DropdownButton<int?>(
                value: _selectedMonth,
                hint: const Text('All Months'),
                isExpanded: true,
                underline: const SizedBox(),
                items: months.map((month) => DropdownMenuItem(
                  value: month,
                  child: Text(month == null ? 'All Months' : _getMonthName(month)),
                )).toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedMonth = value;
                  });
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _getMonthName(int month) {
    const names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return names[month - 1];
  }

  Widget _buildDrawer(BuildContext context) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          DrawerHeader(
            decoration: const BoxDecoration(
              color: Color(0xFF10B981),
            ),
            child: InkWell(
              onTap: () {
                Navigator.pop(context);
                context.go('/');
              },
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Kuberan',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Financial Manager',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.9),
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
            initiallyExpanded: true,
            children: [
              ListTile(
                leading: const Icon(Icons.assessment),
                title: const Text('  Expense Tracker'),
                selected: _tabController.index == 0,
                onTap: () {
                  Navigator.pop(context);
                  _tabController.animateTo(0);
                },
              ),
              ListTile(
                leading: const Icon(Icons.trending_up),
                title: const Text('  Investment Analysis'),
                selected: _tabController.index == 1,
                onTap: () {
                  Navigator.pop(context);
                  _tabController.animateTo(1);
                },
              ),
            ],
          ),
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
