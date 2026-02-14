import 'package:flutter/material.dart';
import '../../widgets/investment_analysis_widget.dart';

/// Investment Analysis Tab - Deep dive into investment income and patterns
/// 
/// FILE LOCATION: frontend/kuberan_app/lib/screens/tabs/investment_analysis_tab.dart
/// 
/// PURPOSE: Displays investment-focused analytics including:
/// - Investment income tracking
/// - Dividend analysis
/// - Investment patterns and trends
/// 
/// DATA LOADING:
/// - Reuses InvestmentAnalysisWidget component
/// - Widget handles its own data fetching from backend
/// - Service File: frontend/kuberan_app/lib/services/financier_service.dart
/// 
/// STATE MANAGEMENT:
/// - Parent FinancierScreen passes year/month filters
/// - Widget refreshes when filters change
class InvestmentAnalysisTab extends StatelessWidget {
  final int? selectedYear;
  final int? selectedMonth;
  final VoidCallback onRefresh;
  
  const InvestmentAnalysisTab({
    super.key,
    this.selectedYear,
    this.selectedMonth,
    required this.onRefresh,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Page header
          const Text(
            'Investment Analysis',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Track investment income, dividends, and patterns',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 24),
          
          // Investment analysis widget
          InvestmentAnalysisWidget(
            year: selectedYear,
            month: selectedMonth,
          ),
        ],
      ),
    );
  }
}
