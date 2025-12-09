/// Model for ticker information from backend
class TickerInfo {
  final String ticker;
  final String name;
  final String? description;
  final String? sector;
  final String? industry;
  final double? marketCap;  // Backend returns double, not int
  final int? totalEmployees;
  final String enrichmentStatus;
  final List<String> metadataSources;
  
  // Additional fields from /stocks/complete endpoint
  final String? phoneNumber;
  final String? address;
  final String? sicCode;
  final String? sicDescription;
  final String? logoUrl;
  final String? iconUrl;
  final String? listDate;
  final int? weightedSharesOutstanding;
  final String? cik;
  final String? compositeFigi;
  final String? homepageUrl;
  final String? primaryExchange;
  final double? currentPrice;
  final String? currency;

  TickerInfo({
    required this.ticker,
    required this.name,
    this.description,
    this.sector,
    this.industry,
    this.marketCap,
    this.totalEmployees,
    required this.enrichmentStatus,
    required this.metadataSources,
    this.phoneNumber,
    this.address,
    this.sicCode,
    this.sicDescription,
    this.logoUrl,
    this.iconUrl,
    this.listDate,
    this.weightedSharesOutstanding,
    this.cik,
    this.compositeFigi,
    this.homepageUrl,
    this.primaryExchange,
    this.currentPrice,
    this.currency,
  });

  factory TickerInfo.fromJson(Map<String, dynamic> json) {
    return TickerInfo(
      ticker: json['ticker'] ?? '',
      name: json['name'] ?? 'Unknown',
      description: json['description'],
      sector: json['sector'],
      industry: json['industry'],
      marketCap: json['market_cap'] != null ? (json['market_cap'] as num).toDouble() : null,
      totalEmployees: json['total_employees'],
      enrichmentStatus: json['enrichment_status'] ?? 'base',
      metadataSources: List<String>.from(json['metadata_sources'] ?? []),
      phoneNumber: json['phone_number'],
      address: json['address'],
      sicCode: json['sic_code'],
      sicDescription: json['sic_description'],
      logoUrl: json['logo_url'],
      iconUrl: json['icon_url'],
      listDate: json['list_date'],
      weightedSharesOutstanding: json['weighted_shares_outstanding'],
      cik: json['cik'],
      compositeFigi: json['composite_figi'],
      homepageUrl: json['homepage_url'],
      primaryExchange: json['primary_exchange'],
      currentPrice: json['current_price'] != null ? (json['current_price'] as num).toDouble() : null,
      currency: json['currency'],
    );
  }

  /// Format market cap for display (e.g., "$2.77T")
  String get formattedMarketCap {
    if (marketCap == null) return 'N/A';
    
    final value = marketCap!;
    if (value >= 1000000000000) {
      return '\$${(value / 1000000000000).toStringAsFixed(2)}T';
    } else if (value >= 1000000000) {
      return '\$${(value / 1000000000).toStringAsFixed(2)}B';
    } else if (value >= 1000000) {
      return '\$${(value / 1000000).toStringAsFixed(2)}M';
    } else {
      return '\$$value';
    }
  }

  /// Format employees for display (e.g., "154K")
  String get formattedEmployees {
    if (totalEmployees == null) return 'N/A';
    
    final value = totalEmployees!;
    if (value >= 1000) {
      return '${(value / 1000).toStringAsFixed(1)}K';
    } else {
      return value.toString();
    }
  }
}

/// Response wrapper for ticker list API
class TickerListResponse {
  final int total;
  final int limit;
  final int offset;
  final List<TickerInfo> tickers;

  TickerListResponse({
    required this.total,
    required this.limit,
    required this.offset,
    required this.tickers,
  });

  factory TickerListResponse.fromJson(Map<String, dynamic> json) {
    return TickerListResponse(
      total: json['total'] ?? 0,
      limit: json['limit'] ?? 50,
      offset: json['skip'] ?? 0,  // Backend uses 'skip' not 'offset'
      tickers: (json['tickers'] as List<dynamic>?)
              ?.map((item) => TickerInfo.fromJson(item))
              .toList() ??
          [],
    );
  }

  int get totalPages => (total / limit).ceil();
  int get currentPage => (offset / limit).floor() + 1;
  bool get hasNextPage => offset + limit < total;
  bool get hasPreviousPage => offset > 0;
}
