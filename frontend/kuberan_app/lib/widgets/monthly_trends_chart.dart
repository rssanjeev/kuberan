import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../services/financier_service.dart';
import 'time_period_selector.dart';

/// Monthly trends chart widget
/// 
/// Displays line chart showing:
/// - Total expenses (red line)
/// - Net cashflow (blue line)
/// 
/// Features:
/// - Time period selector (2m, 6m, ytd)
/// - Responsive sizing
/// - Loading states
/// - Tooltips on hover
class MonthlyTrendsChart extends StatefulWidget {
  final String initialPeriod;

  const MonthlyTrendsChart({
    super.key,
    this.initialPeriod = '6m',
  });

  @override
  State<MonthlyTrendsChart> createState() => _MonthlyTrendsChartState();
}

class _MonthlyTrendsChartState extends State<MonthlyTrendsChart> {
  final FinancierService _service = FinancierService();
  
  bool _isLoading = false;
  String? _errorMessage;
  Map<String, dynamic>? _trendsData;
  late String _selectedPeriod;

  @override
  void initState() {
    super.initState();
    _selectedPeriod = widget.initialPeriod;
    _loadTrends();
  }

  Future<void> _loadTrends() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final data = await _service.getMonthlyTrends(period: _selectedPeriod);
      setState(() {
        _trendsData = data;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load trends: $e';
        _isLoading = false;
      });
    }
  }

  void _onPeriodChanged(String period) {
    setState(() {
      _selectedPeriod = period;
    });
    _loadTrends();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Title
            Text(
              'Monthly Trends',
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            
            // Time period selector
            TimePeriodSelector(
              selectedPeriod: _selectedPeriod,
              onPeriodChanged: _onPeriodChanged,
            ),
            
            const SizedBox(height: 16),
            
            // Chart content
            SizedBox(
              height: 300,
              child: _buildChartContent(theme),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChartContent(ThemeData theme) {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_errorMessage != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 48, color: theme.colorScheme.error),
            const SizedBox(height: 16),
            Text(
              _errorMessage!,
              style: TextStyle(color: theme.colorScheme.error),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _loadTrends,
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_trendsData == null || _trendsData!['data_points'] == 0) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.insert_chart_outlined, size: 48, color: theme.colorScheme.outline),
            const SizedBox(height: 16),
            Text(
              'No data available for selected period',
              style: TextStyle(color: theme.colorScheme.onSurfaceVariant),
            ),
          ],
        ),
      );
    }

    return _buildLineChart(theme);
  }

  Widget _buildLineChart(ThemeData theme) {
    final List<String> months = List<String>.from(_trendsData!['months']);
    final List<double> expenses = List<double>.from(
      _trendsData!['expenses'].map((e) => e is int ? e.toDouble() : e)
    );
    final List<double> cashflow = List<double>.from(
      _trendsData!['cashflow'].map((e) => e is int ? e.toDouble() : e)
    );

    // Find min/max for Y-axis
    final allValues = [...expenses, ...cashflow];
    final minY = allValues.reduce((a, b) => a < b ? a : b);
    final maxY = allValues.reduce((a, b) => a > b ? a : b);
    
    // Add padding to Y-axis range
    final yPadding = (maxY - minY) * 0.1;
    final adjustedMinY = (minY - yPadding).floorToDouble();
    final adjustedMaxY = (maxY + yPadding).ceilToDouble();

    return LineChart(
      LineChartData(
        minY: adjustedMinY,
        maxY: adjustedMaxY,
        lineBarsData: [
          // Expenses line (red)
          LineChartBarData(
            spots: expenses
                .asMap()
                .entries
                .map((e) => FlSpot(e.key.toDouble(), e.value))
                .toList(),
            isCurved: true,
            color: Colors.red.shade400,
            barWidth: 3,
            isStrokeCapRound: true,
            dotData: const FlDotData(show: true),
            belowBarData: BarAreaData(show: false),
          ),
          // Cashflow line (blue)
          LineChartBarData(
            spots: cashflow
                .asMap()
                .entries
                .map((e) => FlSpot(e.key.toDouble(), e.value))
                .toList(),
            isCurved: true,
            color: Colors.blue.shade400,
            barWidth: 3,
            isStrokeCapRound: true,
            dotData: const FlDotData(show: true),
            belowBarData: BarAreaData(show: false),
          ),
        ],
        titlesData: FlTitlesData(
          // Bottom titles (months)
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              interval: 1, // Show label for every month
              getTitlesWidget: (value, meta) {
                if (value.toInt() < 0 || value.toInt() >= months.length) {
                  return const Text('');
                }
                
                // Format month from "2025-01" to "Jan"
                final monthStr = months[value.toInt()];
                try {
                  final date = DateTime.parse('$monthStr-01');
                  final formatted = DateFormat('MMM').format(date);
                  return Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      formatted,
                      style: theme.textTheme.bodySmall,
                    ),
                  );
                } catch (e) {
                  return Text(
                    monthStr,
                    style: theme.textTheme.bodySmall,
                  );
                }
              },
              reservedSize: 32,
            ),
          ),
          // Left titles (dollar amounts)
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                final formatter = NumberFormat.compact();
                return Text(
                  '\$${formatter.format(value)}',
                  style: theme.textTheme.bodySmall,
                );
              },
              reservedSize: 50,
            ),
          ),
          // Hide top and right titles
          topTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          rightTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
        ),
        gridData: FlGridData(
          show: true,
          drawVerticalLine: true,
          verticalInterval: 1, // Show vertical line for every month
          horizontalInterval: (adjustedMaxY - adjustedMinY) / 5,
          getDrawingVerticalLine: (value) {
            return FlLine(
              color: theme.colorScheme.outline.withOpacity(0.1),
              strokeWidth: 1,
            );
          },
          getDrawingHorizontalLine: (value) {
            return FlLine(
              color: theme.colorScheme.outline.withOpacity(0.2),
              strokeWidth: 1,
            );
          },
        ),
        borderData: FlBorderData(
          show: true,
          border: Border(
            bottom: BorderSide(
              color: theme.colorScheme.outline.withOpacity(0.3),
              width: 1,
            ),
            left: BorderSide(
              color: theme.colorScheme.outline.withOpacity(0.3),
              width: 1,
            ),
          ),
        ),
        lineTouchData: LineTouchData(
          enabled: true,
          touchTooltipData: LineTouchTooltipData(
            getTooltipItems: (touchedSpots) {
              return touchedSpots.map((spot) {
                final monthIndex = spot.x.toInt();
                if (monthIndex < 0 || monthIndex >= months.length) {
                  return null;
                }
                
                final monthStr = months[monthIndex];
                final formatter = NumberFormat.currency(symbol: '\$', decimalDigits: 2);
                
                // Determine line type (expenses or cashflow)
                final isExpenses = spot.barIndex == 0;
                final label = isExpenses ? 'Expenses' : 'Cashflow';
                final color = isExpenses ? Colors.red.shade400 : Colors.blue.shade400;
                
                return LineTooltipItem(
                  '$label\n$monthStr\n${formatter.format(spot.y)}',
                  TextStyle(
                    color: color,
                    fontWeight: FontWeight.bold,
                  ),
                );
              }).toList();
            },
          ),
        ),
      ),
    );
  }
}
