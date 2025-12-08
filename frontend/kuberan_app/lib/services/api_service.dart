import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/metadata_stats.dart';

/// Service for communicating with Kuberan backend API
class ApiService {
  static const String baseUrl = 'http://localhost:8000';
  
  final http.Client _client;

  ApiService({http.Client? client}) : _client = client ?? http.Client();

  /// Fetch metadata enrichment statistics
  Future<MetadataStats> getMetadataStats() async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/system/metadata/stats'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Request timeout - backend may be down');
        },
      );

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body) as Map<String, dynamic>;
        return MetadataStats.fromJson(jsonData);
      } else {
        throw Exception('Failed to load stats: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Cannot connect to backend: $e');
    }
  }

  /// Check if backend is healthy
  Future<bool> checkHealth() async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 5));

      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  /// Close HTTP client
  void dispose() {
    _client.close();
  }
}
