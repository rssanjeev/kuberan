import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../services/financier_service.dart';

/// Monthly spending pie chart widget
/// 
/// Displays a pie chart showing spending breakdown by category for a specific month.
/// 
/// Features:
/// - Interactive pie chart with category colors
/// - Category legend
/// - Click to see category details
/// - Loading and error states
class MonthlySpendingPieChart extends StatefulWidget {
  final int? year;
  final int? month;

  const MonthlySpendingPieChart({
    super.key,
    this.year,
    this.month,
  });

  @override
  State<MonthlySpendingPieChart> createState() => _MonthlySpendingPieChartState();
}

class _MonthlySpendingPieChartState extends State<MonthlySpendingPieChart> {
  final FinancierService _service = FinancierService();
  
  bool _isLoading = false;
  String? _errorMessage;
  Map<String, dynamic>? _spendingData;
  int _touchedIndex = -1;
  String _selectedPeriod = 'current'; // 'current', '3m', '6m'

  // Predefined colors for categories
  final List<Color> _categoryColors = [
    Colors.blue,
    Colors.red,
    Colors.green,
    Colors.orange,
    Colors.purple,
    Colors.teal,
    Colors.pink,
    Colors.amber,
    Colors.indigo,
    Colors.cyan,
    Colors.lime,
    Colors.deepOrange,
  ];

  @override
  void initState() {
    super.initState();
    _loadSpendingData();
  }

  @override
  void didUpdateWidget(MonthlySpendingPieChart oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.year != widget.year || oldWidget.month != widget.month) {
      _loadSpendingData();
    }
  }

  Future<void> _loadSpendingData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      Map<String, dynamic> aggregatedData;
      
      if (_selectedPeriod == 'current') {
        // Get current month data (use widget parameters if provided, otherwise current date)
        final targetYear = widget.year ?? DateTime.now().year;
        final targetMonth = widget.month ?? DateTime.now().month;
        print('Fetching current month: $targetYear-$targetMonth');
        aggregatedData = await _service.getSpendingSummary(
          year: targetYear,
          month: targetMonth,
        );
        print('Current month data received: ${aggregatedData['category_breakdown']?.length ?? 0} categories');
      } else {
        // For 3m and 6m, aggregate data from multiple months
        final now = DateTime.now();
        final monthsToAggregate = _selectedPeriod == '3m' ? 3 : 6;
        
        // Aggregate category totals
        Map<String, double> categoryTotals = {};
        double totalSpending = 0.0;
        
        for (int i = 0; i < monthsToAggregate; i++) {
          final targetDate = DateTime(now.year, now.month - i, 1);
          
          try {
            final monthData = await _service.getSpendingSummary(
              year: targetDate.year,
              month: targetDate.month,
            );
            
            if (monthData['category_breakdown'] != null) {
              final categories = monthData['category_breakdown'] as List;
              for (var category in categories) {
                final categoryName = category['category'] as String;
                final amount = (category['amount'] as num).toDouble();
                categoryTotals[categoryName] = (categoryTotals[categoryName] ?? 0) + amount;
                totalSpending += amount;
              }
            }
          } catch (e) {
            // Skip months with no data
            continue;
          }
        }
        
        // Convert aggregated data back to the expected format
        if (categoryTotals.isEmpty) {
          aggregatedData = {
            'category_breakdown': [],
            'total_spending': 0.0,
          };
        } else {
          final categoryBreakdown = categoryTotals.entries.map((entry) {
            final percentage = (entry.value / totalSpending) * 100;
            return {
              'category': entry.key,
              'amount': entry.value,
              'percentage': percentage,
            };
          }).toList();
          
          // Sort by amount descending
          categoryBreakdown.sort((a, b) => (b['amount'] as double).compareTo(a['amount'] as double));
          
          aggregatedData = {
            'category_breakdown': categoryBreakdown,
            'total_spending': totalSpending,
          };
        }
      }
      
      setState(() {
        _spendingData = aggregatedData;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load spending data: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      elevation: 2,
      child: SizedBox(
        height: 424, // Match line chart total height
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
            // Vertical time period selector
            Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                _buildPeriodButton(
                  context,
                  label: 'Current\nMonth',
                  period: 'current',
                  isSelected: _selectedPeriod == 'current',
                ),
                const SizedBox(height: 8),
                _buildPeriodButton(
                  context,
                  label: '3\nMonths',
                  period: '3m',
                  isSelected: _selectedPeriod == '3m',
                ),
                const SizedBox(height: 8),
                _buildPeriodButton(
                  context,
                  label: '6\nMonths',
                  period: '6m',
                  isSelected: _selectedPeriod == '6m',
                ),
              ],
            ),
            const SizedBox(width: 16),
            
            // Chart content
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Title
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Spending by Category',
                        style: theme.textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      if (_selectedPeriod == 'current')
                        Text(
                          DateFormat('MMMM yyyy').format(DateTime.now()),
                          style: theme.textTheme.titleSmall?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        )
                      else
                        Text(
                          _selectedPeriod == '3m' ? 'Last 3 Months' : 'Last 6 Months',
                          style: theme.textTheme.titleSmall?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  
                  // Chart
                  SizedBox(
                    height: 300,
                    child: _buildChartContent(theme),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    ),  // Close SizedBox(height: 424)
  );    // Close Card
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
              onPressed: _loadSpendingData,
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_spendingData == null || 
        _spendingData!['category_breakdown'] == null ||
        (_spendingData!['category_breakdown'] as List).isEmpty) {
      // Determine period description
      String periodText;
      if (_selectedPeriod == 'current') {
        periodText = DateFormat('MMMM yyyy').format(DateTime.now());
      } else if (_selectedPeriod == '3m') {
        periodText = 'the last 3 months';
      } else {
        periodText = 'the last 6 months';
      }
      
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.pie_chart_outline,
              size: 48,
              color: theme.colorScheme.outline.withOpacity(0.5),
            ),
            const SizedBox(height: 16),
            Text(
              'No transactions in $periodText',
              style: theme.textTheme.bodyLarge,
            ),
            const SizedBox(height: 8),
            Text(
              'Try selecting a different time period',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurface.withOpacity(0.6),
              ),
            ),
          ],
        ),
      );
    }

    return _buildPieChart(theme);
  }

  Widget _buildPieChart(ThemeData theme) {
    final List<dynamic> categories = _spendingData!['category_breakdown'];
    final double totalSpent = _spendingData!['total_spending']?.toDouble() ?? 0.0;

    // Filter out Income category and create pie sections
    final filteredCategories = categories
        .where((cat) => cat['category'] != 'Income')
        .toList();

    if (filteredCategories.isEmpty) {
      return Center(
        child: Text(
          'No expense categories found',
          style: TextStyle(color: theme.colorScheme.onSurfaceVariant),
        ),
      );
    }

    final formatter = NumberFormat.currency(symbol: '\$', decimalDigits: 2);

    return Center(
      child: AspectRatio(
        aspectRatio: 1.3,
        child: PieChart(
          PieChartData(
            sections: filteredCategories.asMap().entries.map((entry) {
              final index = entry.key;
              final category = entry.value;
              final amount = (category['amount'] ?? 0.0).toDouble();
              final percentage = (category['percentage'] ?? 0.0).toDouble();
              final categoryName = category['category'] ?? 'Unknown';
              final color = _categoryColors[index % _categoryColors.length];
              final isTouched = index == _touchedIndex;
              final radius = isTouched ? 110.0 : 100.0;
              final fontSize = isTouched ? 16.0 : 14.0;

              return PieChartSectionData(
                value: amount,
                // Show percentage only if >= 4%, or if touched
                title: (percentage >= 4.0 || isTouched) 
                    ? '${percentage.toStringAsFixed(1)}%' 
                    : '',
                color: color,
                radius: radius,
                titleStyle: TextStyle(
                  fontSize: fontSize,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
                // Show tooltip on hover
                badgeWidget: isTouched ? Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.black87,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    '$categoryName\n${formatter.format(amount)}\n${percentage.toStringAsFixed(1)}%',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ) : null,
                badgePositionPercentageOffset: 0.98,
              );
            }).toList(),
            sectionsSpace: 2,
            centerSpaceRadius: 40,
            pieTouchData: PieTouchData(
              touchCallback: (FlTouchEvent event, pieTouchResponse) {
                setState(() {
                  if (!event.isInterestedForInteractions ||
                      pieTouchResponse == null ||
                      pieTouchResponse.touchedSection == null) {
                    _touchedIndex = -1;
                    return;
                  }
                  _touchedIndex = pieTouchResponse.touchedSection!.touchedSectionIndex;
                });
              },
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildPeriodButton(
    BuildContext context, {
    required String label,
    required String period,
    required bool isSelected,
  }) {
    final theme = Theme.of(context);
    
    return SizedBox(
      width: 80,
      height: 60,
      child: ElevatedButton(
        onPressed: () {
          setState(() {
            _selectedPeriod = period;
          });
          _loadSpendingData();
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: isSelected
              ? theme.colorScheme.primary
              : theme.colorScheme.surfaceVariant,
          foregroundColor: isSelected
              ? theme.colorScheme.onPrimary
              : theme.colorScheme.onSurfaceVariant,
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
        child: Text(
          label,
          textAlign: TextAlign.center,
          style: theme.textTheme.labelMedium?.copyWith(
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            fontSize: 11,
          ),
        ),
      ),
    );
  }
}
