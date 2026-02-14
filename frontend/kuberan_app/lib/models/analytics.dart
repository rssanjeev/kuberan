/// Models for comprehensive financial analytics
/// Maps to backend response from /financier/analytics/comprehensive

class ComprehensiveAnalysis {
  final CashFlow cashFlow;
  final List<CategoryBreakdownItem> categoryBreakdown;
  final List<MonthlyCashFlowItem> monthlyCashFlow;
  final List<OutlierTransaction> outliers;
  final SpendingTrends? spendingTrends;
  final List<RecurringPayment> recurringPayments;
  final Map<String, dynamic> financialHealth;

  ComprehensiveAnalysis({
    required this.cashFlow,
    required this.categoryBreakdown,
    required this.monthlyCashFlow,
    required this.outliers,
    this.spendingTrends,
    required this.recurringPayments,
    required this.financialHealth,
  });

  factory ComprehensiveAnalysis.fromJson(Map<String, dynamic> json) {
    return ComprehensiveAnalysis(
      cashFlow: CashFlow.fromJson(json['cash_flow'] as Map<String, dynamic>? ?? {}),
      categoryBreakdown: (json['category_breakdown'] as List? ?? [])
          .map((item) => CategoryBreakdownItem.fromJson(item as Map<String, dynamic>))
          .toList(),
      monthlyCashFlow: (json['monthly_cash_flow'] as List? ?? [])
          .map((item) => MonthlyCashFlowItem.fromJson(item as Map<String, dynamic>))
          .toList(),
      outliers: ((json['outliers'] as Map<String, dynamic>?)?['transactions'] as List? ?? [])
          .map((item) => OutlierTransaction.fromJson(item as Map<String, dynamic>))
          .toList(),
      spendingTrends: json['trend_analysis'] != null
          ? SpendingTrends.fromJson(json['trend_analysis'] as Map<String, dynamic>)
          : null,
      recurringPayments: (json['recurring_payments'] as List? ?? [])
          .map((item) => RecurringPayment.fromJson(item as Map<String, dynamic>))
          .toList(),
      financialHealth: json['financial_health'] as Map<String, dynamic>? ?? {},
    );
  }
}

class CashFlow {
  final double totalIncome;
  final double totalExpenses;
  final double netCashFlow;

  CashFlow({
    required this.totalIncome,
    required this.totalExpenses,
    required this.netCashFlow,
  });

  factory CashFlow.fromJson(Map<String, dynamic> json) {
    return CashFlow(
      totalIncome: (json['total_income'] as num?)?.toDouble() ?? 0.0,
      totalExpenses: (json['total_expenses'] as num?)?.toDouble() ?? 0.0,
      netCashFlow: (json['net_cash_flow'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class CategoryBreakdownItem {
  final String category;
  final double totalAmount;
  final double percentage;
  final int transactionCount;
  final double averageTransaction;

  CategoryBreakdownItem({
    required this.category,
    required this.totalAmount,
    required this.percentage,
    required this.transactionCount,
    required this.averageTransaction,
  });

  factory CategoryBreakdownItem.fromJson(Map<String, dynamic> json) {
    return CategoryBreakdownItem(
      category: json['category'] as String? ?? 'Unknown',
      totalAmount: (json['amount'] as num?)?.toDouble() ?? 0.0,  // Backend uses 'amount' not 'total_amount'
      percentage: (json['percentage'] as num?)?.toDouble() ?? 0.0,
      transactionCount: json['transaction_count'] as int? ?? 0,
      averageTransaction: (json['average_transaction'] as num?)?.toDouble() ?? 0.0,
    );
  }

  String get formattedAmount => '\$${totalAmount.toStringAsFixed(2)}';
  String get formattedPercentage => '${percentage.toStringAsFixed(1)}%';
}

class MonthlyCashFlowItem {
  final String month;
  final double income;
  final double expenses;
  final double netCashFlow;

  MonthlyCashFlowItem({
    required this.month,
    required this.income,
    required this.expenses,
    required this.netCashFlow,
  });

  factory MonthlyCashFlowItem.fromJson(Map<String, dynamic> json) {
    return MonthlyCashFlowItem(
      month: json['month'] as String? ?? '',
      income: (json['income'] as num?)?.toDouble() ?? 0.0,
      expenses: (json['expenses'] as num?)?.toDouble() ?? 0.0,
      netCashFlow: (json['net_cash_flow'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class OutlierTransaction {
  final String date;
  final String merchant;
  final double amount;
  final String? category;
  final double zScore;
  final String reason;

  OutlierTransaction({
    required this.date,
    required this.merchant,
    required this.amount,
    this.category,
    required this.zScore,
    required this.reason,
  });

  factory OutlierTransaction.fromJson(Map<String, dynamic> json) {
    return OutlierTransaction(
      date: json['date'] as String? ?? '',
      merchant: json['merchant'] as String? ?? 'Unknown',
      amount: (json['amount'] as num?)?.toDouble() ?? 0.0,
      category: json['category'] as String?,
      zScore: (json['z_score'] as num?)?.toDouble() ?? 0.0,
      reason: json['reason'] as String? ?? '',
    );
  }

  String get formattedAmount => '\$${amount.toStringAsFixed(2)}';
}

class SpendingTrends {
  final String trend;
  final double slope;
  final String interpretation;

  SpendingTrends({
    required this.trend,
    required this.slope,
    required this.interpretation,
  });

  factory SpendingTrends.fromJson(Map<String, dynamic> json) {
    return SpendingTrends(
      trend: json['trend'] as String? ?? '',
      slope: (json['slope'] as num?)?.toDouble() ?? 0.0,
      interpretation: json['interpretation'] as String? ?? '',
    );
  }
}

class RecurringPayment {
  final String merchant;
  final double averageAmount;
  final String frequency;  // Backend returns string like 'monthly', not int
  final int occurrences;   // Number of times payment occurred
  final bool isStable;     // Whether payment amount is consistent
  final String? category;

  RecurringPayment({
    required this.merchant,
    required this.averageAmount,
    required this.frequency,
    required this.occurrences,
    required this.isStable,
    this.category,
  });

  factory RecurringPayment.fromJson(Map<String, dynamic> json) {
    return RecurringPayment(
      merchant: json['merchant'] as String? ?? 'Unknown',
      averageAmount: (json['average_amount'] as num?)?.toDouble() ?? 0.0,
      frequency: json['frequency'] as String? ?? 'unknown',
      occurrences: json['occurrences'] as int? ?? 0,
      isStable: json['is_stable'] as bool? ?? false,
      category: json['category'] as String?,
    );
  }

  String get formattedAmount => '\$${averageAmount.toStringAsFixed(2)}';
}
