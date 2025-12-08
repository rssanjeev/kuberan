import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:file_picker/file_picker.dart';
import '../../services/financier_service.dart';
import '../../models/analytics.dart';
import '../../models/transaction.dart';
import '../../widgets/upload_dialog.dart';
import '../../widgets/monthly_trends_chart.dart';
import '../../widgets/monthly_spending_pie_chart.dart';

/// Expense Tracker Tab - Cash flow analysis and spending breakdown
/// 
/// FILE LOCATION: frontend/kuberan_app/lib/screens/tabs/expense_tracker_tab.dart
/// 
/// PURPOSE: Displays comprehensive expense analytics including:
/// - Cash flow (income, expenses, net)
/// - Category breakdown with charts
/// - Monthly trends
/// - Financial health indicators
/// 
/// DATA LOADING:
/// - Uses FinancierService to fetch data from backend
/// - API Endpoint: GET /financier/analytics/comprehensive?year={year}&month={month}
/// - Service File: frontend/kuberan_app/lib/services/financier_service.dart
/// - Backend Route: backend/app/routers/financier.py
/// 
/// STATE MANAGEMENT:
/// - Uses StatefulWidget for local state (loading, error, analysis data)
/// - Parent FinancierScreen passes year/month filters
/// - Refreshes when filters change via onRefresh callback
class ExpenseTrackerTab extends StatefulWidget {
  final int? selectedYear;
  final int? selectedMonth;
  final VoidCallback onRefresh;
  
  const ExpenseTrackerTab({
    super.key,
    this.selectedYear,
    this.selectedMonth,
    required this.onRefresh,
  });

  @override
  State<ExpenseTrackerTab> createState() => _ExpenseTrackerTabState();
}

class _ExpenseTrackerTabState extends State<ExpenseTrackerTab> {
  final FinancierService _financierService = FinancierService();
  
  bool _isLoading = false;
  String? _errorMessage;
  ComprehensiveAnalysis? _analysis;
  
  @override
  void initState() {
    super.initState();
    _loadAnalysis();
  }

  @override
  void didUpdateWidget(ExpenseTrackerTab oldWidget) {
    super.didUpdateWidget(oldWidget);
    // Reload when filters change
    if (oldWidget.selectedYear != widget.selectedYear || 
        oldWidget.selectedMonth != widget.selectedMonth) {
      _loadAnalysis();
    }
  }

  Future<void> _loadAnalysis() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final analysis = await _financierService.getComprehensiveAnalysis(
        year: widget.selectedYear,
        month: widget.selectedMonth,
      );

      setState(() {
        _analysis = analysis;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _uploadFile() async {
    // Show upload dialog
    final result = await showDialog<Map<String, dynamic>>(
      context: context,
      builder: (context) => const UploadDialog(),
    );

    if (result == null) return; // User cancelled

    final files = result['files'] as List<PlatformFile>;
    final statementType = result['statement_type'] as String;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    int successCount = 0;
    int totalTransactions = 0;

    try {
      // Upload all files
      for (final file in files) {
        if (file.bytes == null) continue;

        final uploadResult = await _financierService.uploadStatement(
          fileBytes: file.bytes!,
          filename: file.name,
          bank: 'Chase',
          statementType: statementType,
        );

        // Check if duplicate
        if (uploadResult['status'] == 'duplicate') {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(
                  '⚠️ ${file.name}: Already processed (duplicate)',
                ),
                backgroundColor: Colors.orange,
              ),
            );
          }
          continue; // Skip to next file
        }

        // Only count successful uploads
        if (uploadResult['status'] == 'success') {
          successCount++;
          totalTransactions += (uploadResult['transaction_count'] as int?) ?? 0;
        }
      }

      // Show success message
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              '✓ Processed $successCount ${successCount == 1 ? 'file' : 'files'} '
              '($totalTransactions transactions)',
            ),
            backgroundColor: Colors.green,
          ),
        );
      }

      // Reload analysis and notify parent
      await _loadAnalysis();
      widget.onRefresh();
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }

    setState(() {
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_errorMessage != null) {
      return _buildErrorState();
    }

    if (_analysis == null) {
      return _buildEmptyState();
    }

    return _buildDashboard();
  }

  Widget _buildErrorState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            Text(
              _errorMessage ?? 'Unknown error',
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.red),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _loadAnalysis,
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF10B981),
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.upload_file, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            const Text(
              'No financial data yet',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              'Upload your first credit card statement to get started',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _uploadFile,
              icon: const Icon(Icons.cloud_upload),
              label: const Text('Upload PDF Statement'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF10B981),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDashboard() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Upload button
          _buildUploadSection(),
          const SizedBox(height: 24),
          
          // Cash flow cards
          _buildCashFlowCards(),
          const SizedBox(height: 24),
          
          // Charts side-by-side
          LayoutBuilder(
            builder: (context, constraints) {
              // Stack vertically on narrow screens, side-by-side on wider screens
              final isNarrow = constraints.maxWidth < 900;
              
              if (isNarrow) {
                return Column(
                  children: [
                    // Monthly trends chart
                    const MonthlyTrendsChart(
                      initialPeriod: '6m',
                    ),
                    const SizedBox(height: 16),
                    // Monthly spending pie chart
                    MonthlySpendingPieChart(
                      year: widget.selectedYear,
                      month: widget.selectedMonth,
                    ),
                  ],
                );
              } else {
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Monthly trends chart (2/3 width)
                    const Expanded(
                      flex: 2,
                      child: MonthlyTrendsChart(
                        initialPeriod: '6m',
                      ),
                    ),
                    const SizedBox(width: 16),
                    // Monthly spending pie chart (1/3 width)
                    Expanded(
                      flex: 1,
                      child: MonthlySpendingPieChart(
                        year: widget.selectedYear,
                        month: widget.selectedMonth,
                      ),
                    ),
                  ],
                );
              }
            },
          ),
          const SizedBox(height: 24),
          
          // Category breakdown
          if (_analysis!.categoryBreakdown.isNotEmpty) ...[
            _buildCategoryBreakdown(),
            const SizedBox(height: 24),
          ],
          
          // Financial health indicators
          _buildFinancialHealth(),
        ],
      ),
    );
  }

  Widget _buildUploadSection() {
    return ElevatedButton.icon(
      onPressed: _uploadFile,
      icon: const Icon(Icons.cloud_upload, size: 24),
      label: const Text(
        'Upload PDF',
        style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
      ),
      style: ElevatedButton.styleFrom(
        backgroundColor: const Color(0xFF4CAF50),
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(30),
        ),
        elevation: 2,
      ),
    );
  }

  Widget _buildCashFlowCards() {
    final cashFlow = _analysis!.cashFlow;
    
    return LayoutBuilder(
      builder: (context, constraints) {
        final cardWidth = (constraints.maxWidth - 32) / 3;
        
        return Row(
          children: [
            Expanded(
              child: _buildStatCard(
                'Total Income',
                '\$${cashFlow.totalIncome.toStringAsFixed(2)}',
                Icons.arrow_downward,
                Colors.green,
                width: cardWidth,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildStatCard(
                'Total Expenses',
                '\$${cashFlow.totalExpenses.toStringAsFixed(2)}',
                Icons.arrow_upward,
                Colors.red,
                width: cardWidth,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildStatCard(
                'Net Cash Flow',
                '\$${cashFlow.netCashFlow.toStringAsFixed(2)}',
                cashFlow.netCashFlow >= 0 ? Icons.trending_up : Icons.trending_down,
                cashFlow.netCashFlow >= 0 ? Colors.green : Colors.red,
                width: cardWidth,
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon, Color color, {required double width}) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  label,
                  style: const TextStyle(
                    fontSize: 14,
                    color: Colors.grey,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                Icon(icon, color: color, size: 20),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMonthlyCashFlow() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final greenColor = isDarkMode ? Colors.green.shade300 : Colors.green.shade700;
    final redColor = isDarkMode ? Colors.red.shade300 : Colors.red.shade700;
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Monthly Cash Flow',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: DataTable(
                columns: const [
                  DataColumn(label: Text('Month', style: TextStyle(fontWeight: FontWeight.bold))),
                  DataColumn(label: Text('Income', style: TextStyle(fontWeight: FontWeight.bold))),
                  DataColumn(label: Text('Expenses', style: TextStyle(fontWeight: FontWeight.bold))),
                  DataColumn(label: Text('Net', style: TextStyle(fontWeight: FontWeight.bold))),
                ],
                rows: _analysis!.monthlyCashFlow.map((month) {
                  return DataRow(
                    cells: [
                      DataCell(Text(month.month)),
                      DataCell(Text('\$${month.income.toStringAsFixed(2)}', 
                        style: TextStyle(color: greenColor))),
                      DataCell(Text('\$${month.expenses.toStringAsFixed(2)}', 
                        style: TextStyle(color: redColor))),
                      DataCell(Text('\$${month.netCashFlow.toStringAsFixed(2)}',
                        style: TextStyle(
                          color: month.netCashFlow >= 0 ? greenColor : redColor,
                          fontWeight: FontWeight.bold,
                        ))),
                    ],
                  );
                }).toList(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCategoryBreakdown() {
    final allCategories = _analysis!.categoryBreakdown;
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Spending Categories',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                TextButton.icon(
                  onPressed: () {
                    context.push('/financier/transactions', extra: {
                      'year': widget.selectedYear,
                      'month': widget.selectedMonth,
                    });
                  },
                  icon: const Icon(Icons.list_alt, size: 18),
                  label: const Text('View All Transactions'),
                  style: TextButton.styleFrom(
                    foregroundColor: const Color(0xFF10B981),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ...allCategories.map((category) => Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: InkWell(
                onTap: () => _showCategoryTransactionsDialog(category.category),
                borderRadius: BorderRadius.circular(8),
                child: Ink(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              category.category,
                              style: const TextStyle(fontWeight: FontWeight.w500),
                            ),
                            Row(
                              children: [
                                Text(
                                  '${category.formattedAmount} (${category.formattedPercentage})',
                                  style: const TextStyle(fontWeight: FontWeight.bold),
                                ),
                                const SizedBox(width: 4),
                                const Icon(Icons.chevron_right, size: 18, color: Colors.grey),
                              ],
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        LinearProgressIndicator(
                          value: category.percentage / 100,
                          backgroundColor: Colors.grey[200],
                          valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF10B981)),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '${category.transactionCount} transactions • Avg: \$${category.averageTransaction.toStringAsFixed(2)}',
                          style: const TextStyle(fontSize: 12, color: Colors.grey),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            )),
          ],
        ),
      ),
    );
  }

  Widget _buildFinancialHealth() {
    final health = _analysis!.financialHealth;
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Financial Health Indicators',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            if (health['savings_rate'] != null)
              _buildHealthIndicator(
                'Savings Rate',
                '${(health['savings_rate'] * 100).toStringAsFixed(1)}%',
                health['savings_rate'] >= 0.2 ? Colors.green : Colors.orange,
              ),
            if (health['expense_ratio'] != null)
              _buildHealthIndicator(
                'Expense Ratio',
                '${(health['expense_ratio'] * 100).toStringAsFixed(1)}%',
                health['expense_ratio'] <= 0.5 ? Colors.green : Colors.orange,
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildHealthIndicator(String label, String value, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 14)),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              value,
              style: TextStyle(
                color: color,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _showCategoryTransactionsDialog(String category) async {
    // Show loading dialog first
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(
        child: CircularProgressIndicator(),
      ),
    );

    try {
      // Fetch transactions for this category
      final transactions = await _financierService.getTransactions(
        year: widget.selectedYear,
        month: widget.selectedMonth,
        category: category,
        limit: 1000,
      );

      // Close loading dialog
      if (mounted) Navigator.of(context).pop();

      // Show transactions dialog
      if (mounted) {
        showDialog(
          context: context,
          builder: (context) => Dialog(
            child: Container(
              width: MediaQuery.of(context).size.width * 0.9,
              height: MediaQuery.of(context).size.height * 0.8,
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              category,
                              style: const TextStyle(
                                fontSize: 24,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          const SizedBox(height: 4),
                          Text(
                            '${transactions.total} transactions',
                            style: TextStyle(
                              fontSize: 14,
                                color: Colors.grey[600],
                              ),
                            ),
                          ],
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close),
                        onPressed: () => Navigator.of(context).pop(),
                        tooltip: 'Close',
                      ),
                    ],
                  ),
                  const Divider(height: 24),
                  // Transactions list
                  Expanded(
                    child: transactions.transactions.isEmpty
                        ? Center(
                            child: Text(
                              'No transactions found',
                              style: TextStyle(
                                fontSize: 16,
                                color: Colors.grey[600],
                              ),
                            ),
                          )
                        : ListView.builder(
                            itemCount: transactions.transactions.length,
                            itemBuilder: (context, index) {
                              final txn = transactions.transactions[index];
                              final isCredit = txn.transactionType == 'credit';
                              
                              return Card(
                                margin: const EdgeInsets.only(bottom: 8),
                                child: ListTile(
                                  leading: CircleAvatar(
                                    backgroundColor: isCredit
                                        ? Colors.green.withOpacity(0.1)
                                        : Colors.red.withOpacity(0.1),
                                    child: Icon(
                                      isCredit ? Icons.arrow_downward : Icons.arrow_upward,
                                      color: isCredit ? Colors.green : Colors.red,
                                      size: 20,
                                    ),
                                  ),
                                  title: Text(
                                    txn.merchantName,
                                    style: const TextStyle(
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                  subtitle: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        '${txn.transactionDate}/${txn.statementMonth}${txn.merchantLocation != null && txn.merchantLocation!.isNotEmpty ? ' • ${txn.merchantLocation}' : ''}',
                                        style: const TextStyle(fontSize: 12),
                                      ),
                                      const SizedBox(height: 4),
                                      Row(
                                        children: [
                                          const Text(
                                            'Category: ',
                                            style: TextStyle(
                                              fontSize: 11,
                                              fontWeight: FontWeight.w500,
                                            ),
                                          ),
                                          Text(
                                            txn.category,
                                            style: TextStyle(
                                              fontSize: 11,
                                              color: Colors.blue[700],
                                              fontWeight: FontWeight.w600,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                  trailing: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Text(
                                        txn.formattedAmount,
                                        style: TextStyle(
                                          fontWeight: FontWeight.bold,
                                          fontSize: 16,
                                          color: isCredit ? Colors.green : Colors.red,
                                        ),
                                      ),
                                      // Only show edit button for MongoDB transactions (with _id)
                                      if (txn.transactionId.isNotEmpty) ...[
                                        const SizedBox(width: 8),
                                        IconButton(
                                          icon: const Icon(Icons.edit, size: 18),
                                          onPressed: () => _editTransactionCategory(
                                            txn,
                                            category,
                                          ),
                                          tooltip: 'Edit Category',
                                          padding: EdgeInsets.zero,
                                          constraints: const BoxConstraints(),
                                        ),
                                      ],
                                    ],
                                  ),
                                ),
                              );
                            },
                          ),
                  ),
                ],
              ),
            ),
          ),
        );
      }
    } catch (e) {
      // Close loading dialog
      if (mounted) Navigator.of(context).pop();
      
      // Show error dialog
      if (mounted) {
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Error'),
            content: Text('Failed to load transactions: $e'),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('OK'),
              ),
            ],
          ),
        );
      }
    }
  }

  Future<void> _editTransactionCategory(
    Transaction txn,
    String currentCategory,
  ) async {
    // Comprehensive list of all possible categories (using Set to ensure uniqueness)
    final categoriesSet = {
      'Alcohol & Wine',
      'Car Payment',
      'Car Wash & Maintenance',
      'Coffee & Cafes',
      'Credit Card Payments',
      'Entertainment',
      'Farm Stands & Local',
      'Food',
      'Food Delivery',
      'Gas & Fuel',
      'Groceries',
      'Health & Pharmacy',
      'Home & Garden',
      'Housing',
      'Ice Cream & Desserts',
      'Income',
      'Insurance',
      'Interest & Fees',
      'Investments',
      'Loan Payments',
      'Other',
      'Personal Transfers',
      'Remittances',
      'Restaurants & Dining',
      'Services & Fees',
      'Shopping & Retail',
      'Transportation',
      'Utilities',
      'Zelle Received',
    };
    
    // Convert to sorted list
    final categories = categoriesSet.toList()..sort();

    if (categories.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('No categories available'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    // State for dialog
    String? selectedCategory = currentCategory;
    bool updateAllFromMerchant = false;

    // Show category selection dialog
    final result = await showDialog<Map<String, dynamic>>(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: const Text('Edit Transaction Category'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Change category for:'),
              const SizedBox(height: 8),
              Text(
                txn.merchantName,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: selectedCategory,
                decoration: const InputDecoration(
                  labelText: 'Category',
                  border: OutlineInputBorder(),
                ),
                items: categories.map((cat) {
                  return DropdownMenuItem(
                    value: cat,
                    child: Text(cat),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    selectedCategory = value;
                  });
                },
              ),
              const SizedBox(height: 16),
              CheckboxListTile(
                value: updateAllFromMerchant,
                onChanged: (value) {
                  setState(() {
                    updateAllFromMerchant = value ?? false;
                  });
                },
                title: const Text(
                  'Apply to all transactions from this merchant',
                  style: TextStyle(fontSize: 14),
                ),
                subtitle: const Text(
                  'Update past transactions and set default for future',
                  style: TextStyle(fontSize: 12),
                ),
                controlAffinity: ListTileControlAffinity.leading,
                contentPadding: EdgeInsets.zero,
                dense: true,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: selectedCategory != null
                  ? () {
                      Navigator.of(context).pop({
                        'category': selectedCategory,
                        'updateAll': updateAllFromMerchant,
                      });
                    }
                  : null,
              child: const Text('Save'),
            ),
          ],
        ),
      ),
    );

    // Update category if changed
    if (result != null) {
      final newCategory = result['category'] as String?;
      final updateAll = result['updateAll'] as bool? ?? false;

      if (newCategory != null && newCategory != currentCategory) {
        try {
          // Show loading indicator
          showDialog(
            context: context,
            barrierDismissible: false,
            builder: (context) => const Center(
              child: CircularProgressIndicator(),
            ),
          );

          // Update category via API with bulk update option
          final updateResult = await _financierService.updateTransactionCategory(
            txn.transactionId,
            newCategory,
            updateAllFromMerchant: updateAll,
          );

          // Close loading indicator
          if (mounted) Navigator.of(context).pop();

          // Reload analytics to reflect the change
          await _loadAnalysis();

          // Show success message with count
          if (mounted) {
            final updatedCount = updateResult['updated_count'] as int? ?? 1;
            final merchant = updateResult['merchant'] as String? ?? txn.merchantName;
            
            String message;
            if (updateAll && updatedCount > 1) {
              message = 'Updated $updatedCount transactions from $merchant to "$newCategory"';
            } else {
              message = 'Category updated to "$newCategory"';
            }

            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(message),
                backgroundColor: Colors.green,
                duration: Duration(seconds: updateAll ? 4 : 2),
              ),
            );
          }
        } catch (e) {
          // Close loading indicator
          if (mounted) Navigator.of(context).pop();

          // Show error message
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Error updating category: $e'),
                backgroundColor: Colors.red,
                duration: const Duration(seconds: 3),
              ),
            );
          }
        }
      }
    }
  }
}
