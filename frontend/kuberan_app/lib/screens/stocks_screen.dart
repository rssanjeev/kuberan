import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../services/stock_service.dart';
import '../models/ticker_info.dart';

/// Stocks page - displays table of enriched tickers with search and pagination
class StocksScreen extends StatefulWidget {
  const StocksScreen({super.key});

  @override
  State<StocksScreen> createState() => _StocksScreenState();
}

class _StocksScreenState extends State<StocksScreen> {
  final StockService _stockService = StockService();
  final TextEditingController _searchController = TextEditingController();
  
  bool _isLoading = true;
  String? _errorMessage;
  TickerListResponse? _response;
  int _currentOffset = 0;
  final int _limit = 50;
  String? _searchQuery;
  String _sortBy = 'market_cap';
  String _sortOrder = 'desc';

  @override
  void initState() {
    super.initState();
    _loadTickers();
  }

  @override
  void dispose() {
    _searchController.dispose();
    _stockService.dispose();
    super.dispose();
  }

  Future<void> _loadTickers() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final response = await _stockService.getTickers(
        limit: _limit,
        offset: _currentOffset,
        enrichmentStatus: 'foundation', // Only show enriched tickers
        search: _searchQuery,
        sortBy: _sortBy,
        sortOrder: _sortOrder,
      );

      setState(() {
        _response = response;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  void _onSearch(String query) {
    setState(() {
      _searchQuery = query.isEmpty ? null : query;
      _currentOffset = 0; // Reset to first page
    });
    _loadTickers();
  }

  void _onSort(String columnName) {
    setState(() {
      if (_sortBy == columnName) {
        // Toggle sort order if same column
        _sortOrder = _sortOrder == 'asc' ? 'desc' : 'asc';
      } else {
        // New column, default to descending
        _sortBy = columnName;
        _sortOrder = 'desc';
      }
      _currentOffset = 0; // Reset to first page
    });
    _loadTickers();
  }

  void _nextPage() {
    if (_response?.hasNextPage ?? false) {
      setState(() {
        _currentOffset += _limit;
      });
      _loadTickers();
    }
  }

  void _previousPage() {
    if (_response?.hasPreviousPage ?? false) {
      setState(() {
        _currentOffset -= _limit;
      });
      _loadTickers();
    }
  }

  void _showTickerDetails(TickerInfo ticker) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        maxChildSize: 0.9,
        minChildSize: 0.4,
        expand: false,
        builder: (context, scrollController) => Container(
          padding: const EdgeInsets.all(24),
          child: ListView(
            controller: scrollController,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    ticker.ticker,
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
              Text(
                ticker.name,
                style: TextStyle(fontSize: 18, color: Colors.grey.shade700),
              ),
              const SizedBox(height: 24),
              if (ticker.description != null) ...[
                const Text(
                  'Description',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Text(ticker.description!),
                const SizedBox(height: 16),
              ],
              _buildDetailRow('Sector', ticker.sector ?? 'N/A'),
              _buildDetailRow('Industry', ticker.industry ?? 'N/A'),
              _buildDetailRow('Market Cap', ticker.formattedMarketCap),
              _buildDetailRow('Employees', ticker.formattedEmployees),
              _buildDetailRow('Status', ticker.enrichmentStatus),
              _buildDetailRow(
                'Sources',
                ticker.metadataSources.join(', '),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(
            child: Text(value),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Stock Tracker'),
      ),
      drawer: _buildDrawer(),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Search box
            TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search by ticker or company name...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          _onSearch('');
                        },
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              onSubmitted: _onSearch,
            ),
            const SizedBox(height: 16),
            
            // Table or loading state
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _errorMessage != null
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(Icons.error_outline, size: 48, color: Colors.red),
                              const SizedBox(height: 16),
                              Text(
                                'Error loading stocks',
                                style: TextStyle(fontSize: 18, color: Colors.grey.shade700),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                _errorMessage!,
                                style: TextStyle(color: Colors.grey.shade600),
                              ),
                            ],
                          ),
                        )
                      : _response?.tickers.isEmpty ?? true
                          ? Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  const Icon(Icons.inbox, size: 48, color: Colors.grey),
                                  const SizedBox(height: 16),
                                  Text(
                                    'No stocks found',
                                    style: TextStyle(fontSize: 18, color: Colors.grey.shade700),
                                  ),
                                ],
                              ),
                            )
                          : _buildTickerTable(),
            ),
            
            // Pagination controls
            if (_response != null && _response!.tickers.isNotEmpty)
              _buildPagination(),
          ],
        ),
      ),
    );
  }

  Widget _buildDrawer() {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          DrawerHeader(
            decoration: const BoxDecoration(
              color: Color(0xFF3B82F6),
            ),
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
                  'Stock Tracker',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.9),
                    fontSize: 16,
                  ),
                ),
              ],
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
          ListTile(
            leading: const Icon(Icons.show_chart),
            title: const Text('Stocks'),
            selected: true,
            onTap: () {
              Navigator.pop(context);
            },
          ),
          ListTile(
            leading: const Icon(Icons.account_balance_wallet),
            title: const Text('Financier'),
            onTap: () {
              Navigator.pop(context);
              context.go('/financier');
            },
          ),
        ],
      ),
    );
  }

  Widget _buildTickerTable() {
    return LayoutBuilder(
      builder: (context, constraints) {
        // Calculate responsive column widths
        final availableWidth = constraints.maxWidth - 40; // Account for padding
        final tickerWidth = availableWidth * 0.10;
        final companyWidth = availableWidth * 0.40;
        final sectorWidth = availableWidth * 0.20;
        final marketCapWidth = availableWidth * 0.15;
        final employeesWidth = availableWidth * 0.15;

        return Container(
          padding: const EdgeInsets.only(bottom: 80),
          child: SingleChildScrollView(
            scrollDirection: Axis.vertical,
            child: DataTable(
              columnSpacing: 20,
              headingRowHeight: 56,
              dataRowMinHeight: 48,
              dataRowMaxHeight: 64,
              sortColumnIndex: _sortBy == 'ticker' ? 0 : _sortBy == 'name' ? 1 : _sortBy == 'sector' ? 2 : _sortBy == 'market_cap' ? 3 : _sortBy == 'total_employees' ? 4 : null,
              sortAscending: _sortOrder == 'asc',
              columns: [
                DataColumn(
                  label: SizedBox(
                    width: tickerWidth,
                    child: const Text('Ticker', style: TextStyle(fontWeight: FontWeight.bold)),
                  ),
                  onSort: (columnIndex, ascending) => _onSort('ticker'),
                ),
                DataColumn(
                  label: SizedBox(
                    width: companyWidth,
                    child: const Text('Company', style: TextStyle(fontWeight: FontWeight.bold)),
                  ),
                  onSort: (columnIndex, ascending) => _onSort('name'),
                ),
                DataColumn(
                  label: SizedBox(
                    width: sectorWidth,
                    child: const Text('Sector', style: TextStyle(fontWeight: FontWeight.bold)),
                  ),
                  onSort: (columnIndex, ascending) => _onSort('sector'),
                ),
                DataColumn(
                  label: SizedBox(
                    width: marketCapWidth,
                    child: const Text('Market Cap', style: TextStyle(fontWeight: FontWeight.bold)),
                  ),
                  onSort: (columnIndex, ascending) => _onSort('market_cap'),
                ),
                DataColumn(
                  label: SizedBox(
                    width: employeesWidth,
                    child: const Text('Employees', style: TextStyle(fontWeight: FontWeight.bold)),
                  ),
                  onSort: (columnIndex, ascending) => _onSort('total_employees'),
                ),
              ],
              rows: _response!.tickers.map((ticker) {
                return DataRow(
                  cells: [
                    DataCell(
                      SizedBox(
                        width: tickerWidth,
                        child: Text(
                          ticker.ticker,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF3B82F6),
                          ),
                        ),
                      ),
                      onTap: () => _showTickerDetails(ticker),
                    ),
                    DataCell(
                      SizedBox(
                        width: companyWidth,
                        child: Text(
                          ticker.name,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      onTap: () => _showTickerDetails(ticker),
                    ),
                    DataCell(
                      SizedBox(
                        width: sectorWidth,
                        child: Text(ticker.sector ?? 'N/A'),
                      ),
                      onTap: () => _showTickerDetails(ticker),
                    ),
                    DataCell(
                      SizedBox(
                        width: marketCapWidth,
                        child: Text(ticker.formattedMarketCap),
                      ),
                      onTap: () => _showTickerDetails(ticker),
                    ),
                    DataCell(
                      SizedBox(
                        width: employeesWidth,
                        child: Text(ticker.formattedEmployees),
                      ),
                      onTap: () => _showTickerDetails(ticker),
                    ),
                  ],
                );
              }).toList(),
            ),
          ),
        );
      },
    );
  }

  Widget _buildPagination() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.2),
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          ElevatedButton.icon(
            onPressed: _response!.hasPreviousPage ? _previousPage : null,
            icon: const Icon(Icons.chevron_left),
            label: const Text('Previous'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF3B82F6),
              foregroundColor: Colors.white,
            ),
          ),
          Text(
            'Page ${_response!.currentPage}',
            style: const TextStyle(fontSize: 14),
          ),
          ElevatedButton.icon(
            onPressed: _response!.hasNextPage ? _nextPage : null,
            icon: const Icon(Icons.chevron_right),
            label: const Text('Next'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF3B82F6),
              foregroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );
  }
}
