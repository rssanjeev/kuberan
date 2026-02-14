import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../services/financier_service.dart';
import '../models/transaction.dart';

/// Transactions List Screen - View all transactions with filtering
class TransactionsListScreen extends StatefulWidget {
  final int? initialYear;
  final int? initialMonth;
  final String? initialCategory;

  const TransactionsListScreen({
    super.key,
    this.initialYear,
    this.initialMonth,
    this.initialCategory,
  });

  @override
  State<TransactionsListScreen> createState() => _TransactionsListScreenState();
}

class _TransactionsListScreenState extends State<TransactionsListScreen> {
  final FinancierService _financierService = FinancierService();
  
  bool _isLoading = false;
  String? _errorMessage;
  TransactionListResponse? _transactions;
  
  int? _selectedYear;
  int? _selectedMonth;
  String? _selectedCategory;
  List<String> _categories = [];
  
  @override
  void initState() {
    super.initState();
    _selectedYear = widget.initialYear;
    _selectedMonth = widget.initialMonth;
    _selectedCategory = widget.initialCategory;
    _loadCategories();
    _loadTransactions();
  }

  Future<void> _loadCategories() async {
    try {
      final categories = await _financierService.getCategories();
      setState(() {
        _categories = categories;
      });
    } catch (e) {
      // Categories are optional, don't block UI
    }
  }

  Future<void> _loadTransactions() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final transactions = await _financierService.getTransactions(
        year: _selectedYear,
        month: _selectedMonth,
        category: _selectedCategory,
        limit: 1000, // Get more transactions
      );

      setState(() {
        _transactions = transactions;
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
    final title = _selectedCategory != null 
        ? '$_selectedCategory Transactions'
        : 'All Transactions';
    
    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadTransactions,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: Column(
        children: [
          _buildFilters(),
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _errorMessage != null
                    ? _buildErrorState()
                    : _transactions == null || _transactions!.transactions.isEmpty
                        ? _buildEmptyState()
                        : _buildTransactionsList(),
          ),
        ],
      ),
    );
  }

  Widget _buildFilters() {
    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Filters',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<int?>(
                    value: _selectedYear,
                    decoration: const InputDecoration(
                      labelText: 'Year',
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    ),
                    items: [
                      const DropdownMenuItem(value: null, child: Text('All Years')),
                      DropdownMenuItem(value: 2025, child: const Text('2025')),
                      DropdownMenuItem(value: 2024, child: const Text('2024')),
                    ],
                    onChanged: (value) {
                      setState(() {
                        _selectedYear = value;
                      });
                      _loadTransactions();
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: DropdownButtonFormField<int?>(
                    value: _selectedMonth,
                    decoration: const InputDecoration(
                      labelText: 'Month',
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    ),
                    items: [
                      const DropdownMenuItem(value: null, child: Text('All Months')),
                      ...List.generate(12, (i) => i + 1).map((month) {
                        final monthName = [
                          'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
                        ][month - 1];
                        return DropdownMenuItem(
                          value: month,
                          child: Text(monthName),
                        );
                      }),
                    ],
                    onChanged: (value) {
                      setState(() {
                        _selectedMonth = value;
                      });
                      _loadTransactions();
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  flex: 2,
                  child: DropdownButtonFormField<String?>(
                    value: _selectedCategory,
                    decoration: const InputDecoration(
                      labelText: 'Category',
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    ),
                    items: [
                      const DropdownMenuItem(value: null, child: Text('All Categories')),
                      ..._categories.map((category) => DropdownMenuItem(
                        value: category,
                        child: Text(category),
                      )),
                    ],
                    onChanged: (value) {
                      setState(() {
                        _selectedCategory = value;
                      });
                      _loadTransactions();
                    },
                  ),
                ),
              ],
            ),
            if (_selectedYear != null || _selectedMonth != null || _selectedCategory != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: TextButton.icon(
                  onPressed: () {
                    setState(() {
                      _selectedYear = null;
                      _selectedMonth = null;
                      _selectedCategory = null;
                    });
                    _loadTransactions();
                  },
                  icon: const Icon(Icons.clear),
                  label: const Text('Clear Filters'),
                ),
              ),
          ],
        ),
      ),
    );
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
            const Text(
              'Error Loading Transactions',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              _errorMessage ?? 'Unknown error',
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _loadTransactions,
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
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
            const Icon(Icons.receipt_long, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            const Text(
              'No Transactions Found',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              _selectedYear != null || _selectedMonth != null || _selectedCategory != null
                  ? 'Try adjusting your filters'
                  : 'Upload a statement to get started',
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTransactionsList() {
    final transactions = _transactions!.transactions;
    
    return Column(
      children: [
        // Summary header
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          color: Colors.grey[100],
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '${transactions.length} transaction${transactions.length == 1 ? '' : 's'}',
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              Text(
                'Total: \$${_transactions!.totalAmount.toStringAsFixed(2)}',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF10B981),
                ),
              ),
            ],
          ),
        ),
        
        // Transactions list
        Expanded(
          child: ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: transactions.length,
            separatorBuilder: (context, index) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final txn = transactions[index];
              return _buildTransactionTile(txn);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildTransactionTile(Transaction txn) {
    final isIncome = txn.category == 'Income';
    final isInvestment = txn.category == 'Investments';
    
    Color categoryColor = const Color(0xFF10B981);
    if (isIncome) {
      categoryColor = Colors.blue;
    } else if (isInvestment) {
      categoryColor = Colors.purple;
    }
    
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(vertical: 8, horizontal: 0),
      leading: CircleAvatar(
        backgroundColor: categoryColor.withOpacity(0.1),
        child: Icon(
          _getCategoryIcon(txn.category),
          color: categoryColor,
          size: 20,
        ),
      ),
      title: Text(
        txn.merchantName,
        style: const TextStyle(fontWeight: FontWeight.w500),
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      ),
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (txn.merchantLocation != null)
            Text(
              txn.merchantLocation!,
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            ),
          const SizedBox(height: 4),
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: categoryColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  txn.category,
                  style: TextStyle(
                    fontSize: 11,
                    color: categoryColor,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Text(
                '${txn.statementMonth.toString().padLeft(2, '0')}/${txn.transactionDate.padLeft(2, '0')}/${txn.statementYear}',
                style: TextStyle(fontSize: 11, color: Colors.grey[600]),
              ),
            ],
          ),
        ],
      ),
      trailing: Text(
        '\$${txn.amount.toStringAsFixed(2)}',
        style: TextStyle(
          fontWeight: FontWeight.bold,
          fontSize: 16,
          color: isIncome ? Colors.blue : Colors.black87,
        ),
      ),
    );
  }

  IconData _getCategoryIcon(String category) {
    switch (category.toLowerCase()) {
      case 'income':
        return Icons.attach_money;
      case 'investments':
        return Icons.trending_up;
      case 'housing':
        return Icons.home;
      case 'groceries':
        return Icons.shopping_cart;
      case 'restaurants & dining':
        return Icons.restaurant;
      case 'gas & fuel':
        return Icons.local_gas_station;
      case 'shopping & retail':
        return Icons.shopping_bag;
      case 'utilities':
        return Icons.lightbulb;
      case 'health & pharmacy':
        return Icons.local_hospital;
      case 'entertainment':
        return Icons.movie;
      case 'transportation':
        return Icons.directions_car;
      default:
        return Icons.receipt;
    }
  }
}
