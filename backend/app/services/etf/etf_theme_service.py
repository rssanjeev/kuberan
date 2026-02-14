"""
ETF Theme & Sector Analysis Service.

Provides sector exposure analysis, thematic ETF discovery, and geographic allocation.

SECURITY: No sensitive data handling required.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from app.core.logging_config import get_logger
from app.services.etf.etf_profile_service import etf_profile_service
from app.repositories.provider_repository import provider_repository

logger = get_logger(__name__)


class ETFThemeService:
    """
    Service for ETF sector, theme, and geographic analysis.
    
    Features:
    - Sector exposure analysis across ETFs
    - Thematic ETF discovery (ESG, tech, growth, etc.)
    - Geographic allocation analysis
    - Industry concentration metrics
    """
    
    # Standard sector classifications (GICS Level 1)
    STANDARD_SECTORS = [
        "Technology",
        "Healthcare",
        "Financials",
        "Consumer Discretionary",
        "Communication Services",
        "Industrials",
        "Consumer Staples",
        "Energy",
        "Utilities",
        "Real Estate",
        "Materials"
    ]
    
    # Investment themes taxonomy
    INVESTMENT_THEMES = {
        "esg": ["ESG", "Sustainable", "Clean Energy", "Green", "Social Responsibility"],
        "technology": ["Technology", "Software", "Cloud", "AI", "Cybersecurity", "Semiconductor"],
        "growth": ["Growth", "Innovation", "Disruptive", "Emerging"],
        "value": ["Value", "Dividend", "Income", "Quality"],
        "defensive": ["Defensive", "Low Volatility", "Minimum Volatility", "Conservative"],
        "international": ["International", "Global", "Emerging Markets", "Developed Markets", "Ex-US"],
        "fixed_income": ["Bond", "Treasury", "Corporate Bond", "Fixed Income"],
        "real_estate": ["Real Estate", "REIT", "Property"],
        "commodities": ["Commodity", "Gold", "Energy", "Materials"],
        "smart_beta": ["Smart Beta", "Factor", "Multi-Factor", "Momentum", "Quality"]
    }
    
    # Geographic regions
    GEOGRAPHIC_REGIONS = {
        "north_america": ["United States", "Canada", "North America"],
        "europe": ["Europe", "European Union", "UK", "Germany", "France"],
        "asia_pacific": ["Asia", "Pacific", "Japan", "China", "India", "Australia"],
        "emerging_markets": ["Emerging Markets", "BRICS", "Developing"],
        "latin_america": ["Latin America", "Brazil", "Mexico"],
        "middle_east_africa": ["Middle East", "Africa", "Israel"]
    }
    
    async def get_sector_exposure(
        self,
        sector: str,
        min_exposure: float = 0.05,
        sort_by: str = "exposure"
    ) -> Dict[str, Any]:
        """
        Find all ETFs with significant exposure to a specific sector.
        
        Args:
            sector: Sector name (e.g., "Technology", "Healthcare")
            min_exposure: Minimum sector exposure threshold (default 5%)
            sort_by: Sort order - "exposure" or "assets"
            
        Returns:
            List of ETFs with sector exposure details
            
        Example:
            >>> result = await theme_service.get_sector_exposure("Technology", min_exposure=0.20)
            >>> print(len(result['etfs']))
            25  # ETFs with >20% tech exposure
        """
        logger.info(
            "Finding ETFs with sector exposure",
            extra={"sector": sector, "min_exposure": min_exposure}
        )
        
        # Normalize sector name
        sector_normalized = self._normalize_sector_name(sector)
        
        if not sector_normalized:
            raise ValueError(f"Invalid sector: {sector}. Must be one of: {', '.join(self.STANDARD_SECTORS)}")
        
        try:
            # For demo purposes, return sample ETFs with sector exposure
            # In production, this would query the database for ETF profiles
            sample_etfs = await self._get_sample_etfs_by_sector(sector_normalized, min_exposure)
            
            # Sort results
            if sort_by == "exposure":
                sample_etfs.sort(key=lambda x: x['sector_exposure_pct'], reverse=True)
            elif sort_by == "assets":
                sample_etfs.sort(key=lambda x: x['net_assets'], reverse=True)
            
            result = {
                "sector": sector_normalized,
                "min_exposure_threshold": min_exposure,
                "min_exposure_threshold_pct": round(min_exposure * 100, 2),
                "etfs_found": len(sample_etfs),
                "etfs": sample_etfs,
                "summary": {
                    "average_exposure_pct": round(
                        sum(e['sector_exposure_pct'] for e in sample_etfs) / len(sample_etfs) if sample_etfs else 0,
                        2
                    ),
                    "highest_exposure": sample_etfs[0] if sample_etfs else None,
                    "total_assets_usd": sum(e['net_assets'] for e in sample_etfs)
                },
                "calculation_timestamp": datetime.now().isoformat()
            }
            
            logger.info(
                "Sector exposure analysis complete",
                extra={
                    "sector": sector_normalized,
                    "etfs_found": len(sample_etfs)
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Failed to analyze sector exposure",
                extra={"sector": sector, "error": str(e)},
                exc_info=True
            )
            raise
    
    async def find_thematic_etfs(
        self,
        theme: str,
        min_assets: Optional[float] = None,
        max_expense_ratio: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Find ETFs by investment theme.
        
        Args:
            theme: Investment theme (e.g., "esg", "technology", "growth")
            min_assets: Minimum net assets in USD (optional)
            max_expense_ratio: Maximum expense ratio as decimal (optional)
            
        Returns:
            List of ETFs matching the theme with details
            
        Example:
            >>> result = await theme_service.find_thematic_etfs(
            ...     "esg", min_assets=1e9, max_expense_ratio=0.005
            ... )
            >>> print(result['etfs'][0]['ticker'])
            'ESGU'
        """
        logger.info(
            "Finding thematic ETFs",
            extra={"theme": theme, "min_assets": min_assets}
        )
        
        # Normalize theme
        theme_normalized = theme.lower().strip()
        
        if theme_normalized not in self.INVESTMENT_THEMES:
            available_themes = ', '.join(self.INVESTMENT_THEMES.keys())
            raise ValueError(f"Invalid theme: {theme}. Available themes: {available_themes}")
        
        try:
            # Get sample thematic ETFs
            thematic_etfs = await self._get_sample_thematic_etfs(theme_normalized)
            
            # Apply filters
            filtered_etfs = thematic_etfs
            
            if min_assets:
                filtered_etfs = [e for e in filtered_etfs if e['net_assets'] >= min_assets]
            
            if max_expense_ratio:
                filtered_etfs = [e for e in filtered_etfs if e['expense_ratio'] <= max_expense_ratio]
            
            # Sort by assets (largest first)
            filtered_etfs.sort(key=lambda x: x['net_assets'], reverse=True)
            
            result = {
                "theme": theme_normalized,
                "theme_description": self._get_theme_description(theme_normalized),
                "theme_keywords": self.INVESTMENT_THEMES[theme_normalized],
                "filters_applied": {
                    "min_assets": min_assets,
                    "max_expense_ratio": max_expense_ratio
                },
                "etfs_found": len(filtered_etfs),
                "etfs": filtered_etfs,
                "summary": {
                    "total_assets_usd": sum(e['net_assets'] for e in filtered_etfs),
                    "average_expense_ratio": round(
                        sum(e['expense_ratio'] for e in filtered_etfs) / len(filtered_etfs) if filtered_etfs else 0,
                        6
                    ),
                    "average_expense_ratio_pct": round(
                        sum(e['expense_ratio'] for e in filtered_etfs) / len(filtered_etfs) * 100 if filtered_etfs else 0,
                        4
                    ),
                    "largest_etf": filtered_etfs[0] if filtered_etfs else None
                },
                "calculation_timestamp": datetime.now().isoformat()
            }
            
            logger.info(
                "Thematic ETF search complete",
                extra={
                    "theme": theme_normalized,
                    "etfs_found": len(filtered_etfs)
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Failed to find thematic ETFs",
                extra={"theme": theme, "error": str(e)},
                exc_info=True
            )
            raise
    
    async def analyze_geographic_allocation(
        self,
        tickers: List[str],
        aggregation: str = "weighted"
    ) -> Dict[str, Any]:
        """
        Analyze geographic allocation across multiple ETFs.
        
        Args:
            tickers: List of ETF ticker symbols
            aggregation: "weighted" (by portfolio weight) or "equal" (equal weight)
            
        Returns:
            Geographic allocation breakdown with regional exposure
            
        Example:
            >>> result = await theme_service.analyze_geographic_allocation(
            ...     ["VOO", "VXUS", "VWO"]
            ... )
            >>> print(result['geographic_breakdown']['north_america_pct'])
            65.5  # North America allocation
        """
        logger.info(
            "Analyzing geographic allocation",
            extra={"tickers": tickers, "count": len(tickers)}
        )
        
        if not tickers:
            raise ValueError("At least one ticker is required")
        
        if len(tickers) > 20:
            raise ValueError("Maximum 20 tickers allowed")
        
        try:
            # Get geographic data for each ETF
            etf_geo_data = []
            
            for ticker in tickers:
                geo_data = await self._get_etf_geographic_allocation(ticker)
                if geo_data:
                    etf_geo_data.append(geo_data)
                else:
                    logger.warning(
                        "Could not get geographic data",
                        extra={"ticker": ticker}
                    )
            
            if not etf_geo_data:
                raise ValueError("No geographic data available for provided tickers")
            
            # Calculate aggregate allocation
            if aggregation == "weighted":
                # Use actual portfolio weights (equal if not provided)
                weight_per_etf = 1.0 / len(etf_geo_data)
                for data in etf_geo_data:
                    data['portfolio_weight'] = weight_per_etf
            else:
                # Equal weight
                for data in etf_geo_data:
                    data['portfolio_weight'] = 1.0 / len(etf_geo_data)
            
            # Aggregate geographic allocations
            aggregate_allocation = {}
            for region in self.GEOGRAPHIC_REGIONS.keys():
                aggregate_allocation[region] = sum(
                    data['geographic_allocation'].get(region, 0) * data['portfolio_weight']
                    for data in etf_geo_data
                )
            
            # Calculate concentrations
            total_allocation = sum(aggregate_allocation.values())
            if total_allocation > 0:
                geographic_breakdown_pct = {
                    f"{region}_pct": round((value / total_allocation) * 100, 2)
                    for region, value in aggregate_allocation.items()
                }
            else:
                geographic_breakdown_pct = {}
            
            # Find dominant region
            dominant_region = max(aggregate_allocation.items(), key=lambda x: x[1]) if aggregate_allocation else (None, 0)
            
            # Calculate diversification score
            diversification_score = self._calculate_geographic_diversification(aggregate_allocation)
            
            result = {
                "tickers": tickers,
                "etfs_analyzed": len(etf_geo_data),
                "aggregation_method": aggregation,
                "geographic_breakdown": geographic_breakdown_pct,
                "absolute_allocation": {
                    region: round(value, 4)
                    for region, value in aggregate_allocation.items()
                },
                "dominant_region": {
                    "region": dominant_region[0],
                    "allocation_pct": round((dominant_region[1] / total_allocation * 100) if total_allocation > 0 else 0, 2)
                } if dominant_region[0] else None,
                "diversification": diversification_score,
                "individual_etfs": etf_geo_data,
                "calculation_timestamp": datetime.now().isoformat()
            }
            
            logger.info(
                "Geographic allocation analysis complete",
                extra={
                    "tickers": len(tickers),
                    "dominant_region": dominant_region[0] if dominant_region else None
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Failed to analyze geographic allocation",
                extra={"tickers": tickers, "error": str(e)},
                exc_info=True
            )
            raise
    
    # -------------------- Helper Methods --------------------
    
    def _normalize_sector_name(self, sector: str) -> Optional[str]:
        """Normalize sector name to standard GICS classification."""
        sector_lower = sector.lower().strip()
        
        for standard_sector in self.STANDARD_SECTORS:
            if sector_lower in standard_sector.lower():
                return standard_sector
        
        return None
    
    async def _get_sample_etfs_by_sector(
        self,
        sector: str,
        min_exposure: float
    ) -> List[Dict[str, Any]]:
        """Get sample ETFs with sector exposure (demo data)."""
        
        # Sample data based on sector
        sector_etfs = {
            "Technology": [
                {"ticker": "XLK", "name": "Technology Select Sector SPDR Fund", "sector_exposure_pct": 100.0, "net_assets": 63000000000, "expense_ratio": 0.0010},
                {"ticker": "VGT", "name": "Vanguard Information Technology ETF", "sector_exposure_pct": 100.0, "net_assets": 73000000000, "expense_ratio": 0.0010},
                {"ticker": "QQQ", "name": "Invesco QQQ Trust", "sector_exposure_pct": 49.5, "net_assets": 285000000000, "expense_ratio": 0.0020},
                {"ticker": "FTEC", "name": "Fidelity MSCI Information Technology ETF", "sector_exposure_pct": 100.0, "net_assets": 13000000000, "expense_ratio": 0.0008},
                {"ticker": "VOO", "name": "Vanguard S&P 500 ETF", "sector_exposure_pct": 31.7, "net_assets": 515000000000, "expense_ratio": 0.0003},
            ],
            "Healthcare": [
                {"ticker": "XLV", "name": "Health Care Select Sector SPDR Fund", "sector_exposure_pct": 100.0, "net_assets": 40000000000, "expense_ratio": 0.0010},
                {"ticker": "VHT", "name": "Vanguard Health Care ETF", "sector_exposure_pct": 100.0, "net_assets": 18000000000, "expense_ratio": 0.0010},
                {"ticker": "IYH", "name": "iShares U.S. Healthcare ETF", "sector_exposure_pct": 100.0, "net_assets": 3500000000, "expense_ratio": 0.0039},
                {"ticker": "FHLC", "name": "Fidelity MSCI Health Care ETF", "sector_exposure_pct": 100.0, "net_assets": 2800000000, "expense_ratio": 0.0008},
                {"ticker": "VOO", "name": "Vanguard S&P 500 ETF", "sector_exposure_pct": 12.3, "net_assets": 515000000000, "expense_ratio": 0.0003},
            ],
            "Financials": [
                {"ticker": "XLF", "name": "Financial Select Sector SPDR Fund", "sector_exposure_pct": 100.0, "net_assets": 48000000000, "expense_ratio": 0.0010},
                {"ticker": "VFH", "name": "Vanguard Financials ETF", "sector_exposure_pct": 100.0, "net_assets": 12000000000, "expense_ratio": 0.0010},
                {"ticker": "IYF", "name": "iShares U.S. Financials ETF", "sector_exposure_pct": 100.0, "net_assets": 4200000000, "expense_ratio": 0.0039},
                {"ticker": "VOO", "name": "Vanguard S&P 500 ETF", "sector_exposure_pct": 13.1, "net_assets": 515000000000, "expense_ratio": 0.0003},
            ],
            "Energy": [
                {"ticker": "XLE", "name": "Energy Select Sector SPDR Fund", "sector_exposure_pct": 100.0, "net_assets": 32000000000, "expense_ratio": 0.0010},
                {"ticker": "VDE", "name": "Vanguard Energy ETF", "sector_exposure_pct": 100.0, "net_assets": 7500000000, "expense_ratio": 0.0010},
                {"ticker": "IYE", "name": "iShares U.S. Energy ETF", "sector_exposure_pct": 100.0, "net_assets": 1800000000, "expense_ratio": 0.0039},
                {"ticker": "VOO", "name": "Vanguard S&P 500 ETF", "sector_exposure_pct": 3.4, "net_assets": 515000000000, "expense_ratio": 0.0003},
            ],
        }
        
        # Get ETFs for this sector
        etfs = sector_etfs.get(sector, [])
        
        # Filter by minimum exposure
        filtered = [
            etf for etf in etfs
            if etf['sector_exposure_pct'] >= min_exposure * 100
        ]
        
        return filtered
    
    async def _get_sample_thematic_etfs(self, theme: str) -> List[Dict[str, Any]]:
        """Get sample thematic ETFs (demo data)."""
        
        thematic_etfs = {
            "esg": [
                {"ticker": "ESGU", "name": "iShares MSCI USA ESG Optimized ETF", "net_assets": 15000000000, "expense_ratio": 0.0015, "theme_focus": "ESG Broad"},
                {"ticker": "VSGX", "name": "Vanguard ESG International Stock ETF", "net_assets": 8000000000, "expense_ratio": 0.0012, "theme_focus": "ESG International"},
                {"ticker": "ESGV", "name": "Vanguard ESG U.S. Stock ETF", "net_assets": 12000000000, "expense_ratio": 0.0009, "theme_focus": "ESG U.S."},
                {"ticker": "SUSA", "name": "iShares MSCI USA ESG Select ETF", "net_assets": 4500000000, "expense_ratio": 0.0025, "theme_focus": "ESG Select"},
            ],
            "technology": [
                {"ticker": "XLK", "name": "Technology Select Sector SPDR Fund", "net_assets": 63000000000, "expense_ratio": 0.0010, "theme_focus": "Broad Tech"},
                {"ticker": "VGT", "name": "Vanguard Information Technology ETF", "net_assets": 73000000000, "expense_ratio": 0.0010, "theme_focus": "IT Sector"},
                {"ticker": "SOXX", "name": "iShares Semiconductor ETF", "net_assets": 14000000000, "expense_ratio": 0.0035, "theme_focus": "Semiconductors"},
                {"ticker": "HACK", "name": "ETFMG Prime Cyber Security ETF", "net_assets": 2800000000, "expense_ratio": 0.0060, "theme_focus": "Cybersecurity"},
                {"ticker": "CLOU", "name": "Global X Cloud Computing ETF", "net_assets": 1200000000, "expense_ratio": 0.0068, "theme_focus": "Cloud Computing"},
            ],
            "growth": [
                {"ticker": "VUG", "name": "Vanguard Growth ETF", "net_assets": 145000000000, "expense_ratio": 0.0004, "theme_focus": "Large Cap Growth"},
                {"ticker": "IVW", "name": "iShares S&P 500 Growth ETF", "net_assets": 45000000000, "expense_ratio": 0.0018, "theme_focus": "S&P 500 Growth"},
                {"ticker": "VONG", "name": "Vanguard Russell 1000 Growth ETF", "net_assets": 28000000000, "expense_ratio": 0.0008, "theme_focus": "Russell Growth"},
                {"ticker": "ARKK", "name": "ARK Innovation ETF", "net_assets": 6500000000, "expense_ratio": 0.0075, "theme_focus": "Disruptive Innovation"},
            ],
            "value": [
                {"ticker": "VTV", "name": "Vanguard Value ETF", "net_assets": 115000000000, "expense_ratio": 0.0004, "theme_focus": "Large Cap Value"},
                {"ticker": "IVE", "name": "iShares S&P 500 Value ETF", "net_assets": 25000000000, "expense_ratio": 0.0018, "theme_focus": "S&P 500 Value"},
                {"ticker": "VONV", "name": "Vanguard Russell 1000 Value ETF", "net_assets": 22000000000, "expense_ratio": 0.0008, "theme_focus": "Russell Value"},
                {"ticker": "VYM", "name": "Vanguard High Dividend Yield ETF", "net_assets": 58000000000, "expense_ratio": 0.0006, "theme_focus": "Dividend"},
            ],
            "defensive": [
                {"ticker": "USMV", "name": "iShares MSCI USA Min Vol Factor ETF", "net_assets": 28000000000, "expense_ratio": 0.0015, "theme_focus": "Min Volatility"},
                {"ticker": "SPLV", "name": "Invesco S&P 500 Low Volatility ETF", "net_assets": 11000000000, "expense_ratio": 0.0025, "theme_focus": "Low Volatility"},
                {"ticker": "EEMV", "name": "iShares MSCI EM Min Vol Factor ETF", "net_assets": 3200000000, "expense_ratio": 0.0025, "theme_focus": "EM Low Vol"},
            ],
            "international": [
                {"ticker": "VXUS", "name": "Vanguard Total International Stock ETF", "net_assets": 72000000000, "expense_ratio": 0.0007, "theme_focus": "Ex-US Broad"},
                {"ticker": "VEA", "name": "Vanguard FTSE Developed Markets ETF", "net_assets": 120000000000, "expense_ratio": 0.0005, "theme_focus": "Developed Markets"},
                {"ticker": "VWO", "name": "Vanguard FTSE Emerging Markets ETF", "net_assets": 95000000000, "expense_ratio": 0.0008, "theme_focus": "Emerging Markets"},
                {"ticker": "IEFA", "name": "iShares Core MSCI EAFE ETF", "net_assets": 115000000000, "expense_ratio": 0.0007, "theme_focus": "EAFE"},
            ],
        }
        
        return thematic_etfs.get(theme, [])
    
    def _get_theme_description(self, theme: str) -> str:
        """Get description for investment theme."""
        descriptions = {
            "esg": "Environmental, Social, and Governance focused investments",
            "technology": "Technology sector and innovation-focused ETFs",
            "growth": "Growth-oriented equities with high earnings potential",
            "value": "Value stocks and dividend-focused investments",
            "defensive": "Low volatility and defensive investment strategies",
            "international": "Non-US and global market exposure",
            "fixed_income": "Bond and fixed income securities",
            "real_estate": "Real estate and REIT investments",
            "commodities": "Commodity and hard asset exposure",
            "smart_beta": "Factor-based and rules-based strategies"
        }
        return descriptions.get(theme, "Investment theme")
    
    async def _get_etf_geographic_allocation(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get geographic allocation for an ETF (demo data)."""
        
        # Sample geographic allocations
        geographic_data = {
            "VOO": {
                "ticker": "VOO",
                "name": "Vanguard S&P 500 ETF",
                "geographic_allocation": {
                    "north_america": 1.0,
                    "europe": 0.0,
                    "asia_pacific": 0.0,
                    "emerging_markets": 0.0,
                    "latin_america": 0.0,
                    "middle_east_africa": 0.0
                }
            },
            "VTI": {
                "ticker": "VTI",
                "name": "Vanguard Total Stock Market ETF",
                "geographic_allocation": {
                    "north_america": 1.0,
                    "europe": 0.0,
                    "asia_pacific": 0.0,
                    "emerging_markets": 0.0,
                    "latin_america": 0.0,
                    "middle_east_africa": 0.0
                }
            },
            "VXUS": {
                "ticker": "VXUS",
                "name": "Vanguard Total International Stock ETF",
                "geographic_allocation": {
                    "north_america": 0.03,
                    "europe": 0.40,
                    "asia_pacific": 0.42,
                    "emerging_markets": 0.12,
                    "latin_america": 0.02,
                    "middle_east_africa": 0.01
                }
            },
            "VEA": {
                "ticker": "VEA",
                "name": "Vanguard FTSE Developed Markets ETF",
                "geographic_allocation": {
                    "north_america": 0.02,
                    "europe": 0.49,
                    "asia_pacific": 0.46,
                    "emerging_markets": 0.0,
                    "latin_america": 0.02,
                    "middle_east_africa": 0.01
                }
            },
            "VWO": {
                "ticker": "VWO",
                "name": "Vanguard FTSE Emerging Markets ETF",
                "geographic_allocation": {
                    "north_america": 0.0,
                    "europe": 0.05,
                    "asia_pacific": 0.78,
                    "emerging_markets": 1.0,
                    "latin_america": 0.10,
                    "middle_east_africa": 0.07
                }
            },
        }
        
        return geographic_data.get(ticker.upper())
    
    def _calculate_geographic_diversification(
        self,
        allocation: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate geographic diversification score."""
        
        # Count regions with meaningful allocation (>5%)
        significant_regions = sum(1 for value in allocation.values() if value > 0.05)
        
        # Calculate concentration (Herfindahl index)
        total = sum(allocation.values())
        if total > 0:
            normalized = [v / total for v in allocation.values()]
            herfindahl = sum(x ** 2 for x in normalized)
            concentration_score = round(herfindahl, 4)
        else:
            concentration_score = 1.0
        
        # Diversification score (0-100, higher is better)
        # Lower concentration = higher diversification
        diversification_score = round((1 - concentration_score) * 100, 1)
        
        if diversification_score >= 70:
            interpretation = "Excellent geographic diversification"
        elif diversification_score >= 50:
            interpretation = "Good geographic diversification"
        elif diversification_score >= 30:
            interpretation = "Moderate geographic diversification"
        else:
            interpretation = "Limited geographic diversification (concentrated)"
        
        return {
            "score": diversification_score,
            "interpretation": interpretation,
            "significant_regions": significant_regions,
            "concentration_index": concentration_score
        }


# Singleton instance
etf_theme_service = ETFThemeService()
