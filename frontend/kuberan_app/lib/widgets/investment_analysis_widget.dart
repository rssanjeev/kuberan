import 'package:flutter/material.dart';
import '../services/financier_service.dart';

/// Investment Analysis Widget - Display rolling investment trends
class InvestmentAnalysisWidget extends StatefulWidget {
  final int? year;
  final int? month;

  const InvestmentAnalysisWidget({
    super.key,
    this.year,
    this.month,
  });

  @override
  State<InvestmentAnalysisWidget> createState() => _InvestmentAnalysisWidgetState();
}

class _InvestmentAnalysisWidgetState extends State<InvestmentAnalysisWidget> {
  final FinancierService _financierService = FinancierService();
  
  bool _isLoading = false;
  String? _errorMessage;
  Map<String, dynamic>? _investmentData;
  int _selectedMonthsBack = 12;

  @override
  void initState() {
    super.initState();
    _loadInvestmentAnalysis();
  }

  @override
  void didUpdateWidget(InvestmentAnalysisWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.year != widget.year || oldWidget.month != widget.month) {
      _loadInvestmentAnalysis();
    }
  }

  Future<void> _loadInvestmentAnalysis() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final data = await _financierService.getInvestmentAnalysis(
        year: widget.year,
        month: widget.month,
        monthsBack: _selectedMonthsBack,
      );

      setState(() {
        _investmentData = data;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Row(
                  children: [
                    Icon(Icons.trending_up, color: Colors.purple),
                    SizedBox(width: 8),
                    Text(
                      'Investment Analysis',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                DropdownButton<int>(
                  value: _selectedMonthsBack,
                  items: const [
                    DropdownMenuItem(value: 3, child: Text('3 months')),
                    DropdownMenuItem(value: 6, child: Text('6 months')),
                    DropdownMenuItem(value: 12, child: Text('12 months')),
                    DropdownMenuItem(value: 24, child: Text('24 months')),
                  ],
                  onChanged: (value) {
                    if (value != null) {
                      setState(() {
                        _selectedMonthsBack = value;
                      });
                      _loadInvestmentAnalysis();
                    }
                  },
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (_isLoading)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(32),
                  child: CircularProgressIndicator(),
                ),
              )
            else if (_errorMessage != null)
              _buildErrorState()
            else if (_investmentData == null)
              _buildEmptyState()
            else
              _buildAnalysisContent(),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Icon(Icons.error_outline, color: Colors.red, size: 48),
            const SizedBox(height: 8),
            Text(
              'Error loading investment data',
              style: TextStyle(color: Colors.grey[600]),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Icon(Icons.trending_up, color: Colors.grey, size: 48),
            const SizedBox(height: 8),
            Text(
              'No investment data available',
              style: TextStyle(color: Colors.grey[600]),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAnalysisContent() {
    // Return empty state if data is null
    if (_investmentData == null) {
      return _buildEmptyState();
    }
    
    // Safely extract data with null checks
    final summary = (_investmentData!['summary'] as Map<String, dynamic>?) ?? {};
    final trends = (_investmentData!['trends'] as Map<String, dynamic>?) ?? {};
    final monthlyBreakdown = (_investmentData!['monthly_breakdown'] as List<dynamic>?) ?? [];
    final topDestinations = (_investmentData!['top_destinations'] as List<dynamic>?) ?? [];
    final insights = (_investmentData!['insights'] as List<dynamic>?) ?? [];
    
    // If no data at all, show empty state
    if (summary.isEmpty && monthlyBreakdown.isEmpty) {
      return _buildEmptyState();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Summary metrics
        _buildSummaryMetrics(summary, trends),
        
        const SizedBox(height: 20),
        const Divider(),
        const SizedBox(height: 16),
        
        // Monthly breakdown
        if (monthlyBreakdown.isNotEmpty) ...[
          const Text(
            'Monthly Contributions',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          _buildMonthlyChart(monthlyBreakdown),
          const SizedBox(height: 20),
        ],
        
        // Top destinations
        if (topDestinations.isNotEmpty) ...[
          const Text(
            'Investment Destinations',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          _buildDestinations(topDestinations),
          const SizedBox(height: 20),
        ],
        
        // Insights
        if (insights.isNotEmpty) ...[
          const Text(
            'Insights',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          _buildInsights(insights),
        ],
      ],
    );
  }

  Widget _buildSummaryMetrics(Map<String, dynamic> summary, Map<String, dynamic> trends) {
    final totalContributions = summary['total_contributions'] ?? 0.0;
    final avgMonthly = summary['average_monthly'] ?? 0.0;
    final projectedAnnual = summary['projected_annual'] ?? 0.0;
    final transactionCount = summary['transaction_count'] ?? 0;
    final trend = trends['direction'] ?? 'stable';
    
    return Row(
      children: [
        Expanded(
          child: _buildMetricCard(
            'Total Invested',
            '\$${totalContributions.toStringAsFixed(2)}',
            Colors.purple,
            Icons.account_balance_wallet,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildMetricCard(
            'Avg Monthly',
            '\$${avgMonthly.toStringAsFixed(2)}',
            Colors.blue,
            Icons.calendar_month,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildMetricCard(
            'Projected Annual',
            '\$${projectedAnnual.toStringAsFixed(0)}',
            Colors.green,
            Icons.trending_up,
          ),
        ),
      ],
    );
  }

  Widget _buildMetricCard(String label, String value, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(height: 8),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[700],
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMonthlyChart(List<dynamic> monthlyBreakdown) {
    final maxAmount = monthlyBreakdown
        .map((m) => m['amount'] as double)
        .reduce((a, b) => a > b ? a : b);

    return Column(
      children: monthlyBreakdown.map<Widget>((month) {
        final monthStr = month['month'] as String;
        final amount = month['amount'] as double;
        final percentage = maxAmount > 0 ? amount / maxAmount : 0.0;
        
        return Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Row(
            children: [
              SizedBox(
                width: 60,
                child: Text(
                  monthStr,
                  style: const TextStyle(fontSize: 12),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Stack(
                  children: [
                    Container(
                      height: 24,
                      decoration: BoxDecoration(
                        color: Colors.grey[200],
                        borderRadius: BorderRadius.circular(4),
                      ),
                    ),
                    FractionallySizedBox(
                      widthFactor: percentage,
                      child: Container(
                        height: 24,
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [Colors.purple, Colors.deepPurple],
                          ),
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ),
                    ),
                    Positioned.fill(
                      child: Center(
                        child: Text(
                          '\$${amount.toStringAsFixed(2)}',
                          style: const TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildDestinations(List<dynamic> destinations) {
    return Column(
      children: destinations.map<Widget>((dest) {
        final destination = dest['destination'] as String;
        final amount = dest['amount'] as double;
        
        return Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: const BoxDecoration(
                      color: Colors.purple,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    destination,
                    style: const TextStyle(fontWeight: FontWeight.w500),
                  ),
                ],
              ),
              Text(
                '\$${amount.toStringAsFixed(2)}',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.purple,
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildInsights(List<dynamic> insights) {
    return Column(
      children: insights.map<Widget>((insight) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(Icons.lightbulb, size: 16, color: Colors.amber),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  insight as String,
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey[700],
                  ),
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}
