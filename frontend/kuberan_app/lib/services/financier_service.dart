import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import '../models/transaction.dart';
import '../models/analytics.dart';

/// Service for Financier API operations
/// 
/// Provides methods for:
/// - Uploading PDF statements
/// - Fetching transactions
/// - Getting comprehensive financial analytics
class FinancierService {
  final String baseUrl = 'http://localhost:8000/financier';
  final http.Client _client = http.Client();

  /// Upload a credit card statement PDF
  /// 
  /// Returns processing summary with transaction counts
  Future<Map<String, dynamic>> uploadStatement({
    required List<int> fileBytes,
    required String filename,
    String bank = 'Chase',
    String statementType = 'credit_card',
  }) async {
    try {
      final uri = Uri.parse('$baseUrl/upload?bank=$bank&statement_type=$statementType');
      final request = http.MultipartRequest('POST', uri);
      
      request.files.add(
        http.MultipartFile.fromBytes(
          'file',
          fileBytes,
          filename: filename,
        ),
      );

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Upload failed: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error uploading statement: $e');
    }
  }

  /// Fetch transactions with optional filtering
  /// 
  /// Parameters:
  /// - year: Filter by statement year
  /// - month: Filter by statement month (1-12)
  /// - category: Filter by category
  /// - limit: Number of results (default 100)
  Future<TransactionListResponse> getTransactions({
    int? year,
    int? month,
    String? category,
    int limit = 100,
  }) async {
    try {
      final queryParams = {
        'limit': limit.toString(),
        if (year != null) 'year': year.toString(),
        if (month != null) 'month': month.toString(),
        if (category != null) 'category': category,
      };

      final uri = Uri.parse('$baseUrl/transactions')
          .replace(queryParameters: queryParams);

      final response = await _client.get(uri);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return TransactionListResponse.fromJson(data);
      } else {
        throw Exception('Failed to load transactions: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching transactions: $e');
    }
  }

  /// Get comprehensive financial analysis
  /// 
  /// Returns deep analytics including:
  /// - Cash flow (income, expenses, net)
  /// - Monthly trends
  /// - Category breakdown
  /// - Outlier detection
  /// - Spending trends
  /// - Recurring payments
  /// - Financial health indicators
  Future<ComprehensiveAnalysis> getComprehensiveAnalysis({
    int? year,
    int? month,
    String? category,
  }) async {
    try {
      final queryParams = {
        if (year != null) 'year': year.toString(),
        if (month != null) 'month': month.toString(),
        if (category != null) 'category': category,
      };

      final uri = Uri.parse('$baseUrl/analytics/comprehensive')
          .replace(queryParameters: queryParams);

      final response = await _client.get(uri);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return ComprehensiveAnalysis.fromJson(data);
      } else {
        throw Exception('Failed to load analysis: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching analysis: $e');
    }
  }

  /// Get spending summary by month
  Future<Map<String, dynamic>> getSpendingSummary({
    int? year,
    int? month,
  }) async {
    try {
      final queryParams = {
        if (year != null) 'year': year.toString(),
        if (month != null) 'month': month.toString(),
      };

      final uri = Uri.parse('$baseUrl/spending/summary')
          .replace(queryParameters: queryParams);

      final response = await _client.get(uri);

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load summary: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching summary: $e');
    }
  }

  /// Get list of all categories
  Future<List<String>> getCategories() async {
    try {
      final uri = Uri.parse('$baseUrl/categories');
      final response = await _client.get(uri);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<String>.from(data['categories'] ?? []);
      } else {
        throw Exception('Failed to load categories: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching categories: $e');
    }
  }

  /// Get rolling investment analysis
  /// 
  /// Returns investment trends over specified period:
  /// - Monthly breakdown
  /// - Total invested
  /// - Average monthly investment
  /// - Trend analysis
  Future<Map<String, dynamic>> getInvestmentAnalysis({
    int? year,
    int? month,
    int monthsBack = 12,
  }) async {
    try {
      final queryParams = {
        if (year != null) 'year': year.toString(),
        if (month != null) 'month': month.toString(),
        'months_back': monthsBack.toString(),
      };

      final uri = Uri.parse('$baseUrl/investments/rolling-analysis')
          .replace(queryParameters: queryParams);

      final response = await _client.get(uri);

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load investment analysis: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching investment analysis: $e');
    }
  }

  /// Update the category of a specific transaction
  /// 
  /// Allows users to correct miscategorized transactions.
  /// 
  /// Optionally update all transactions from the same merchant:
  /// - When updateAllFromMerchant = false: Only update this transaction
  /// - When updateAllFromMerchant = true: Update all transactions from same merchant
  ///   (past and future), and update merchant mapping for auto-categorization
  /// 
  /// Example:
  /// ```dart
  /// // Update single transaction only
  /// await financierService.updateTransactionCategory(
  ///   'transaction_id_123',
  ///   'Food'
  /// );
  /// 
  /// // Update all transactions from this merchant
  /// await financierService.updateTransactionCategory(
  ///   'transaction_id_123',
  ///   'Food',
  ///   updateAllFromMerchant: true
  /// );
  /// ```
  Future<Map<String, dynamic>> updateTransactionCategory(
    String transactionId,
    String newCategory, {
    bool updateAllFromMerchant = false,
  }) async {
    try {
      final response = await _client.put(
        Uri.parse('$baseUrl/transactions/$transactionId/category'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'new_category': newCategory,
          'update_all_from_merchant': updateAllFromMerchant,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {
          'transaction': Transaction.fromJson(data['transaction']),
          'updated_count': data['updated_count'] ?? 1,
          'merchant': data['merchant'] ?? '',
          'updated_all_from_merchant': data['updated_all_from_merchant'] ?? false,
        };
      } else {
        throw Exception('Failed to update category: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Error updating transaction category: $e');
    }
  }

  /// Get monthly expense and cash flow trends
  /// 
  /// Returns aggregated data for charting:
  /// - months: ["2025-07", "2025-08", ...]
  /// - labels: ["Jul", "Aug", ...]
  /// - expenses: [2100.50, 2450.75, ...]
  /// - income: [6827.24, 10240.86, ...]  // Note: August has 3 paydays!
  /// - cashflow: [4726.74, 7790.11, ...]
  /// 
  /// Parameters:
  /// - period: Time period selector
  ///   - '2m': Last 2 months
  ///   - '6m': Last 6 months (default)
  ///   - 'ytd': Year to date
  /// - year: Year for YTD calculation (default: current year)
  Future<Map<String, dynamic>> getMonthlyTrends({
    String period = '6m',
    int? year,
  }) async {
    try {
      final queryParams = {
        'period': period,
        if (year != null) 'year': year.toString(),
      };

      final uri = Uri.parse('$baseUrl/analytics/monthly-trends')
          .replace(queryParameters: queryParams);

      final response = await _client.get(uri);

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load monthly trends: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching monthly trends: $e');
    }
  }
}
