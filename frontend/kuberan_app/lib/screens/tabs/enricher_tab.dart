import 'dart:async';
import 'package:flutter/material.dart';
import '../../widgets/stat_card.dart';
import '../../services/api_service.dart';
import '../../models/metadata_stats.dart';

/// Enricher Tab - Metadata enrichment progress and system status
/// 
/// FILE LOCATION: frontend/kuberan_app/lib/screens/tabs/enricher_tab.dart
/// 
/// PURPOSE: Displays enrichment progress, system status, and stats
/// - Enrichment progress (total/enriched/remaining tickers)
/// - System status (Backend, MongoDB, Foundation Builder)
/// - Auto-refresh with 30-second intervals
/// 
/// DATA LOADING:
/// - Uses ApiService to fetch metadata stats
/// - API Endpoint: GET /system/metadata/stats
/// - Backend Route: backend/app/routers/system.py
/// 
/// STATE MANAGEMENT:
/// - Auto-refresh timer (30 seconds)
/// - Manual refresh button
/// - Pause/resume auto-refresh
class EnricherTab extends StatefulWidget {
  const EnricherTab({super.key});

  @override
  State<EnricherTab> createState() => _EnricherTabState();
}

class _EnricherTabState extends State<EnricherTab> with AutomaticKeepAliveClientMixin {
  bool _isStatusExpanded = false;
  bool _isLoading = true;
  bool _isBackendHealthy = false;
  String? _errorMessage;
  MetadataStats? _stats;
  DateTime? _lastUpdated;
  bool _autoRefreshEnabled = true;
  Timer? _refreshTimer;
  Timer? _tickTimer;
  
  final ApiService _apiService = ApiService();

  @override
  bool get wantKeepAlive => true; // Keep state when switching tabs

  @override
  void initState() {
    super.initState();
    _loadStats();
    _startAutoRefresh();
    _startTickTimer();
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    _tickTimer?.cancel();
    _apiService.dispose();
    super.dispose();
  }

  void _startAutoRefresh() {
    _refreshTimer?.cancel();
    _refreshTimer = Timer.periodic(const Duration(seconds: 30), (timer) {
      if (_autoRefreshEnabled && mounted) {
        _loadStats();
      }
    });
  }

  void _toggleAutoRefresh() {
    setState(() {
      _autoRefreshEnabled = !_autoRefreshEnabled;
    });
  }

  void _startTickTimer() {
    _tickTimer?.cancel();
    _tickTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (mounted && _lastUpdated != null) {
        setState(() {});
      }
    });
  }

  Future<void> _loadStats() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final isHealthy = await _apiService.checkHealth();
      
      if (!isHealthy) {
        throw Exception('Backend is not responding');
      }

      final stats = await _apiService.getMetadataStats();
      
      setState(() {
        _stats = stats;
        _isBackendHealthy = true;
        _isLoading = false;
        _lastUpdated = DateTime.now();
      });
    } catch (e) {
      setState(() {
        _isBackendHealthy = false;
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    super.build(context); // Required for AutomaticKeepAliveClientMixin
    
    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildStatusPanel(),
            const SizedBox(height: 24),
            _buildStatCards(),
            const SizedBox(height: 24),
            _buildProgressIndicator(),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusPanel() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.grey.shade300, width: 1),
      ),
      child: Column(
        children: [
          InkWell(
            onTap: () {
              setState(() {
                _isStatusExpanded = !_isStatusExpanded;
              });
            },
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                children: [
                  const Icon(
                    Icons.check_circle,
                    color: Color(0xFF10B981),
                    size: 24,
                  ),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Text(
                      'System Status',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  Icon(
                    _isStatusExpanded ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down,
                    color: Colors.grey.shade600,
                  ),
                ],
              ),
            ),
          ),
          if (_isStatusExpanded)
            Container(
              decoration: BoxDecoration(
                color: Colors.grey.shade50,
                borderRadius: const BorderRadius.only(
                  bottomLeft: Radius.circular(12),
                  bottomRight: Radius.circular(12),
                ),
              ),
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildStatusRow('Backend', _isBackendHealthy ? 'Connected' : 'Disconnected', _isBackendHealthy ? Colors.green : Colors.red),
                  const SizedBox(height: 8),
                  _buildStatusRow('MongoDB', _isBackendHealthy ? 'Healthy' : 'Unknown', _isBackendHealthy ? Colors.green : Colors.grey),
                  const SizedBox(height: 8),
                  _buildStatusRow('Foundation Builder', _isLoading ? 'Loading...' : 'Active', _isLoading ? Colors.orange : Colors.blue),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Icon(
                        _autoRefreshEnabled ? Icons.autorenew : Icons.pause_circle_outline,
                        size: 16,
                        color: _autoRefreshEnabled ? Colors.green : Colors.grey,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        _autoRefreshEnabled ? 'Auto-refresh: ON (30s)' : 'Auto-refresh: OFF',
                        style: TextStyle(fontSize: 12, color: Colors.grey.shade700),
                      ),
                      const Spacer(),
                      if (_lastUpdated != null)
                        Text(
                          'Updated ${_getTimeSinceUpdate()}',
                          style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                        ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _isLoading ? null : _loadStats,
                          icon: _isLoading
                              ? const SizedBox(
                                  width: 16,
                                  height: 16,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                                  ),
                                )
                              : const Icon(Icons.refresh, size: 18),
                          label: Text(_isLoading ? 'Loading...' : 'Refresh Now'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF3B82F6),
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 10),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      ElevatedButton.icon(
                        onPressed: _toggleAutoRefresh,
                        icon: Icon(_autoRefreshEnabled ? Icons.pause : Icons.play_arrow, size: 18),
                        label: Text(_autoRefreshEnabled ? 'Pause' : 'Resume'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _autoRefreshEnabled ? Colors.grey.shade600 : const Color(0xFF10B981),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 16),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  String _getTimeSinceUpdate() {
    if (_lastUpdated == null) return 'never';
    
    final diff = DateTime.now().difference(_lastUpdated!);
    if (diff.inSeconds < 60) return '${diff.inSeconds}s ago';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    return '${diff.inHours}h ago';
  }

  Widget _buildStatusRow(String label, String status, Color color) {
    return Row(
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 8),
        Text(label, style: const TextStyle(fontWeight: FontWeight.w500)),
        const SizedBox(width: 8),
        Text(status, style: TextStyle(color: Colors.grey.shade600)),
      ],
    );
  }

  Widget _buildStatCards() {
    if (_isLoading) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(48.0),
          child: CircularProgressIndicator(),
        ),
      );
    }

    if (_errorMessage != null) {
      return Card(
        elevation: 2,
        color: Colors.red.shade50,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(color: Colors.red.shade300, width: 1),
        ),
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            children: [
              Icon(Icons.error_outline, color: Colors.red.shade700, size: 48),
              const SizedBox(height: 16),
              Text(
                'Failed to load stats',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.red.shade700),
              ),
              const SizedBox(height: 8),
              Text(_errorMessage!, textAlign: TextAlign.center, style: TextStyle(color: Colors.red.shade600)),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: _loadStats,
                icon: const Icon(Icons.refresh),
                label: const Text('Retry'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red.shade700,
                  foregroundColor: Colors.white,
                ),
              ),
            ],
          ),
        ),
      );
    }

    if (_stats == null) return const Center(child: Text('No data available'));

    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth > 800) {
          return Row(
            children: [
              Expanded(
                child: StatCard(
                  label: 'TOTAL TICKERS',
                  value: _stats!.totalTickers.toString(),
                  subtitle: 'All stocks in database',
                  color: const Color(0xFF3B82F6),
                  icon: Icons.storage,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: StatCard(
                  label: 'ENRICHED TICKERS',
                  value: _stats!.foundationTickers.toString(),
                  subtitle: '${_stats!.enrichmentPercentage.toStringAsFixed(1)}% complete',
                  color: const Color(0xFF10B981),
                  icon: Icons.check_circle_outline,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: StatCard(
                  label: 'REMAINING TICKERS',
                  value: _stats!.remainingTickers.toString(),
                  subtitle: '${(100 - _stats!.enrichmentPercentage).toStringAsFixed(1)}% to go',
                  color: const Color(0xFFEF4444),
                  icon: Icons.pending_outlined,
                ),
              ),
            ],
          );
        } else {
          return Column(
            children: [
              StatCard(
                label: 'TOTAL TICKERS',
                value: _stats!.totalTickers.toString(),
                subtitle: 'All stocks in database',
                color: const Color(0xFF3B82F6),
                icon: Icons.storage,
              ),
              const SizedBox(height: 16),
              StatCard(
                label: 'ENRICHED TICKERS',
                value: _stats!.foundationTickers.toString(),
                subtitle: '${_stats!.enrichmentPercentage.toStringAsFixed(1)}% complete',
                color: const Color(0xFF10B981),
                icon: Icons.check_circle_outline,
              ),
              const SizedBox(height: 16),
              StatCard(
                label: 'REMAINING TICKERS',
                value: _stats!.remainingTickers.toString(),
                subtitle: '${(100 - _stats!.enrichmentPercentage).toStringAsFixed(1)}% to go',
                color: const Color(0xFFEF4444),
                icon: Icons.pending_outlined,
              ),
            ],
          );
        }
      },
    );
  }

  Widget _buildProgressIndicator() {
    if (_isLoading || _errorMessage != null || _stats == null) {
      return const SizedBox.shrink();
    }

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.grey.shade300, width: 1),
      ),
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            const Icon(Icons.trending_up, size: 48, color: Color(0xFF3B82F6)),
            const SizedBox(height: 16),
            Text(
              'Enrichment Progress',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: Colors.grey.shade800),
            ),
            const SizedBox(height: 8),
            Text(
              '${_stats!.enrichmentPercentage.toStringAsFixed(1)}%',
              style: const TextStyle(fontSize: 48, fontWeight: FontWeight.bold, color: Color(0xFF3B82F6)),
            ),
            const SizedBox(height: 16),
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: _stats!.enrichmentPercentage / 100,
                minHeight: 12,
                backgroundColor: Colors.grey.shade200,
                valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF10B981)),
              ),
            ),
            const SizedBox(height: 12),
            Text(
              '${_stats!.foundationTickers} of ${_stats!.totalTickers} tickers enriched',
              style: TextStyle(fontSize: 14, color: Colors.grey.shade600),
            ),
          ],
        ),
      ),
    );
  }
}
