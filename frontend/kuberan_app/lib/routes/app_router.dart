import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../screens/home_screen.dart';
import '../screens/stocks_tabs_screen.dart';
import '../screens/financier_screen.dart';
import '../screens/transactions_list_screen.dart';
import '../screens/settings_screen.dart';

/// Centralized routing configuration using GoRouter
/// Handles navigation between Home, Stocks, Financier, and Settings pages
final GoRouter appRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      name: 'home',
      builder: (context, state) => const HomeScreen(),
    ),
    GoRoute(
      path: '/stocks',
      name: 'stocks',
      builder: (context, state) => const StocksTabsScreen(),
    ),
    GoRoute(
      path: '/financier',
      name: 'financier',
      builder: (context, state) => const FinancierScreen(),
    ),
    GoRoute(
      path: '/financier/transactions',
      name: 'transactions',
      builder: (context, state) {
        // Support both extra (from push) and query parameters (from go)
        final extra = state.extra as Map<String, dynamic>?;
        final yearParam = state.uri.queryParameters['year'];
        final monthParam = state.uri.queryParameters['month'];
        final categoryParam = state.uri.queryParameters['category'];
        
        return TransactionsListScreen(
          initialYear: extra?['year'] as int? ?? 
                       (yearParam != null ? int.tryParse(yearParam) : null),
          initialMonth: extra?['month'] as int? ?? 
                        (monthParam != null ? int.tryParse(monthParam) : null),
          initialCategory: extra?['category'] as String? ?? categoryParam,
        );
      },
    ),
    GoRoute(
      path: '/settings',
      name: 'settings',
      builder: (context, state) => const SettingsScreen(),
    ),
  ],
  errorBuilder: (context, state) => Scaffold(
    appBar: AppBar(title: const Text('Error')),
    body: Center(
      child: Text('Page not found: ${state.uri}'),
    ),
  ),
);
