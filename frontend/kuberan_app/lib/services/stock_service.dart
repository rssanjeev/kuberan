import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/ticker_info.dart';

/// Service for fetching stock/ticker data from backend
class StockService {
  final String baseUrl;
  final http.Client _client;

  StockService({
    this.baseUrl = 'http://localhost:8000',
    http.Client? client,
  }) : _client = client ?? http.Client();

  /// Fetch tickers with optional filtering
  /// 
  /// Parameters:
  /// - limit: Number of results per page (default 50)
  /// - offset: Pagination offset
  /// - enrichmentStatus: Filter by status (foundation, enriched, failed)
  /// - search: Search by ticker symbol or company name
  /// - sortBy: Column to sort by (market_cap, ticker, name)
  /// - sortOrder: Sort direction (asc, desc)
  Future<TickerListResponse> getTickers({
    int limit = 50,
    int offset = 0,
    String? enrichmentStatus,
    String? search,
    String? sortBy,
    String? sortOrder,
  }) async {
    try {
      final queryParams = {
        'limit': limit.toString(),
        'skip': offset.toString(),  // Backend uses 'skip' not 'offset'
        if (enrichmentStatus != null) 'enrichment_status': enrichmentStatus,
        if (search != null && search.isNotEmpty) 'search': search,
        if (sortBy != null) 'sort_by': sortBy,
        if (sortOrder != null) 'sort_order': sortOrder,
      };

      final uri = Uri.parse('$baseUrl/stocks/tickers')
          .replace(queryParameters: queryParams);

      final response = await _client.get(uri);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return TickerListResponse.fromJson(data);
      } else {
        throw Exception('Failed to load tickers: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching tickers: $e');
    }
  }

  /// Fetch complete ticker information with all MASSIVE and YFinance data
  /// 
  /// Returns comprehensive data including:
  /// - Real-time pricing (price, volume, market cap)
  /// - MASSIVE metadata (CIK, FIGI, SIC codes, branding)
  /// - Company info (sector, industry, employees, description)
  /// - Contact details (phone, address, website)
  Future<TickerInfo> getCompleteTickerInfo(String ticker) async {
    try {
      final uri = Uri.parse('$baseUrl/stocks/complete/${ticker.toUpperCase()}');
      final response = await _client.get(uri);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return TickerInfo.fromJson(data);
      } else {
        throw Exception('Failed to load ticker: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching complete ticker info: $e');
    }
  }

  void dispose() {
    _client.close();
  }
}
