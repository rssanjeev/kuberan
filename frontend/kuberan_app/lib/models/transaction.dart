/// Transaction data model for credit card transactions
class Transaction {
  final String transactionId; // MongoDB ObjectId
  final String merchantName;
  final String? merchantLocation;
  final double amount;
  final String transactionType; // 'charge' or 'credit'
  final String category;
  final String transactionDate; // Day of month
  final int statementYear;
  final int statementMonth;
  final String bank;

  Transaction({
    required this.transactionId,
    required this.merchantName,
    this.merchantLocation,
    required this.amount,
    required this.transactionType,
    required this.category,
    required this.transactionDate,
    required this.statementYear,
    required this.statementMonth,
    required this.bank,
  });

  factory Transaction.fromJson(Map<String, dynamic> json) {
    // Handle both API formats: snake_case (database) and camelCase (legacy)
    return Transaction(
      transactionId: json['_id'] ?? json['id'] ?? '',
      merchantName: json['merchant'] ?? json['merchant_name'] ?? '',
      merchantLocation: json['location'] ?? json['merchant_location'],
      amount: (json['amount'] as num).toDouble(),
      transactionType: json['type'] ?? json['transaction_type'] ?? 'charge',
      category: json['category'] ?? 'Uncategorized',
      transactionDate: json['transaction_date'] ?? _extractDay(json['date']),
      statementYear: json['statement_year'] ?? _extractYear(json['date']),
      statementMonth: json['statement_month'] ?? _extractMonth(json['date']),
      bank: json['bank'] ?? '',
    );
  }
  
  static String _extractDay(String? date) {
    if (date == null) return '';
    final parts = date.split('/');
    // Backend format: "YYYY/MM/statement_month/DD"
    // parts[0]=year, parts[1]=month, parts[2]=statement month, parts[3]=day
    return parts.length >= 4 ? parts[3] : (parts.length >= 3 ? parts[2] : '');
  }
  
  static int _extractYear(String? date) {
    if (date == null) return 0;
    final parts = date.split('/');
    return parts.isNotEmpty ? int.tryParse(parts[0]) ?? 0 : 0;
  }
  
  static int _extractMonth(String? date) {
    if (date == null) return 0;
    final parts = date.split('/');
    return parts.length >= 2 ? int.tryParse(parts[1]) ?? 0 : 0;
  }

  String get formattedAmount {
    return '\$${amount.toStringAsFixed(2)}';
  }

  String get statementPeriod {
    final monthNames = [
      '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    return '${monthNames[statementMonth]} $statementYear';
  }

  bool get isCredit => transactionType == 'credit';
  bool get isCharge => transactionType == 'charge';
}

/// Response model for transaction list API
class TransactionListResponse {
  final int total;
  final int returned;
  final List<Transaction> transactions;

  TransactionListResponse({
    required this.total,
    required this.returned,
    required this.transactions,
  });

  factory TransactionListResponse.fromJson(Map<String, dynamic> json) {
    final txns = (json['transactions'] as List? ?? [])
        .map((t) => Transaction.fromJson(t))
        .toList();
    
    return TransactionListResponse(
      total: json['count'] ?? txns.length,
      returned: txns.length,
      transactions: txns,
    );
  }
  
  /// Calculate total amount of all transactions
  double get totalAmount {
    return transactions.fold<double>(
      0.0,
      (sum, transaction) => sum + transaction.amount.abs(),
    );
  }
}
