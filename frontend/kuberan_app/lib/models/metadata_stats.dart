/// Data model for metadata enrichment statistics
class MetadataStats {
  final int totalTickers;
  final int baseTickers;
  final int foundationTickers;
  final int enrichedTickers;
  final int failedTickers;

  MetadataStats({
    required this.totalTickers,
    required this.baseTickers,
    required this.foundationTickers,
    required this.enrichedTickers,
    required this.failedTickers,
  });

  /// Calculate enrichment percentage
  double get enrichmentPercentage {
    if (totalTickers == 0) return 0.0;
    return (foundationTickers / totalTickers) * 100;
  }

  /// Calculate remaining tickers
  int get remainingTickers {
    return baseTickers;
  }

  /// Parse from JSON response
  factory MetadataStats.fromJson(Map<String, dynamic> json) {
    final byStatus = json['by_enrichment_status'] as Map<String, dynamic>;
    
    return MetadataStats(
      totalTickers: json['total_tickers'] as int,
      baseTickers: byStatus['base'] as int,
      foundationTickers: byStatus['foundation'] as int,
      enrichedTickers: byStatus['enriched'] as int,
      failedTickers: byStatus['failed'] as int,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'total_tickers': totalTickers,
      'by_enrichment_status': {
        'base': baseTickers,
        'foundation': foundationTickers,
        'enriched': enrichedTickers,
        'failed': failedTickers,
      },
    };
  }
}
