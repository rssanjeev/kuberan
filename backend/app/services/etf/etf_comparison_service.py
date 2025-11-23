"""
ETF Comparison Service

Provides side-by-side comparison of two ETFs:
- Holdings overlap calculation (weighted)
- Sector drift analysis
- Overweight/underweight positions
- Comparison result caching (7-day TTL)

Phase: 2 of 15
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from app.core.logging_config import get_logger
from app.repositories.etf_repository import etf_repository
from app.services.etf.etf_profile_service import etf_profile_service
from app.models.provider import ETFComparison

logger = get_logger(__name__)


class ETFComparisonService:
    """
    Service for comparing two ETFs.
    
    Comparison includes:
    - Holdings overlap by weight
    - Common vs unique holdings
    - Sector allocation drift
    - Overweight/underweight positions
    """
    
    async def compare_etfs(
        self,
        ticker1: str,
        ticker2: str,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Compare two ETFs side-by-side.
        
        Algorithm:
        1. Fetch both ETF profiles (from cache or API)
        2. Calculate overlap by weight: sum(min(weight1[stock], weight2[stock]))
        3. Identify common holdings and unique holdings
        4. Calculate sector drift: sector1[sector] - sector2[sector]
        5. Find overweight/underweight positions
        6. Cache result for 7 days
        
        Args:
            ticker1: First ETF ticker symbol
            ticker2: Second ETF ticker symbol
            force_refresh: If True, bypass cache and fetch fresh data
            
        Returns:
            Complete comparison with overlap, drift, and position analysis
            
        Raises:
            ValueError: If tickers are invalid or identical
            
        Example:
            >>> result = await compare_etfs("SPY", "QQQ")
            >>> print(result['overlap_by_weight'])
            0.52  # 52% overlap
        """
        # Input validation
        if not ticker1 or not isinstance(ticker1, str):
            raise ValueError("ticker1 must be a non-empty string")
        if not ticker2 or not isinstance(ticker2, str):
            raise ValueError("ticker2 must be a non-empty string")
        
        ticker1 = ticker1.upper().strip()
        ticker2 = ticker2.upper().strip()
        
        if not ticker1.isalnum() or len(ticker1) > 5:
            raise ValueError(f"Invalid ticker1 format: {ticker1}")
        if not ticker2.isalnum() or len(ticker2) > 5:
            raise ValueError(f"Invalid ticker2 format: {ticker2}")
        
        if ticker1 == ticker2:
            raise ValueError(f"Cannot compare ETF to itself: {ticker1}")
        
        logger.info(
            "Comparing ETFs",
            extra={"ticker1": ticker1, "ticker2": ticker2, "force_refresh": force_refresh}
        )
        
        # Check cache first (unless force_refresh)
        if not force_refresh:
            # Create comparison key (alphabetically sorted)
            comparison_key = "_".join(sorted([ticker1, ticker2]))
            cached_comparison = await etf_repository.get_cached_comparison(comparison_key)
            if cached_comparison:
                logger.info(
                    "Retrieved comparison from cache",
                    extra={"ticker1": ticker1, "ticker2": ticker2}
                )
                return self._comparison_to_dict(cached_comparison)
        
        # Fetch both ETF profiles
        profile1 = await etf_profile_service.get_etf_profile(ticker1, force_refresh)
        profile2 = await etf_profile_service.get_etf_profile(ticker2, force_refresh)
        
        # Calculate comparison metrics
        overlap_data = self._calculate_overlap(profile1, profile2)
        sector_drift = self._calculate_sector_drift(profile1, profile2)
        position_analysis = self._analyze_positions(profile1, profile2, overlap_data)
        
        # Create comparison object
        comparison_key = "_".join(sorted([ticker1, ticker2]))
        comparison = ETFComparison(
            ticker1=ticker1,
            ticker2=ticker2,
            comparison_key=comparison_key,
            overlap_by_weight=overlap_data['overlap_by_weight'],
            overlapping_holdings_count=overlap_data['common_count'],
            ticker1_in_ticker2_pct=overlap_data['common_count'] / len(profile1['holdings']['complete_list']) if profile1['holdings']['complete_list'] else 0,
            ticker2_in_ticker1_pct=overlap_data['common_count'] / len(profile2['holdings']['complete_list']) if profile2['holdings']['complete_list'] else 0,
            overlapping_holdings=overlap_data['common_holdings'][:100],  # Top 100
            overweight_holdings=position_analysis['overweight_in_etf1'][:50],  # Top 50
            underweight_holdings=position_analysis['overweight_in_etf2'][:50],  # Top 50
            sector_drift={s['sector']: s['drift'] for s in sector_drift},
            comparison_date=datetime.utcnow(),
            ticker1_stats={
                'total_holdings': len(profile1['holdings']['complete_list']),
                'sectors': len(profile1.get('sectors', []))
            },
            ticker2_stats={
                'total_holdings': len(profile2['holdings']['complete_list']),
                'sectors': len(profile2.get('sectors', []))
            }
        )
        
        # Save to cache
        saved_comparison = await etf_repository.save_comparison(comparison)
        
        logger.info(
            "ETF comparison completed",
            extra={
                "ticker1": ticker1,
                "ticker2": ticker2,
                "overlap": overlap_data['overlap_by_weight'],
                "common_holdings": overlap_data['common_count']
            }
        )
        
        return self._comparison_to_dict(saved_comparison)
    
    def _calculate_overlap(
        self,
        profile1: Dict[str, Any],
        profile2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate holdings overlap between two ETFs.
        
        Overlap is calculated by weight:
        overlap = sum(min(weight1[ticker], weight2[ticker])) for all common tickers
        
        Args:
            profile1: First ETF profile
            profile2: Second ETF profile
            
        Returns:
            Overlap metrics including common and unique holdings
        """
        # Build weight dictionaries
        holdings1 = {h['symbol']: h['weight'] for h in profile1['holdings']['complete_list']}
        holdings2 = {h['symbol']: h['weight'] for h in profile2['holdings']['complete_list']}
        
        # Find common and unique tickers
        tickers1 = set(holdings1.keys())
        tickers2 = set(holdings2.keys())
        common_tickers = tickers1.intersection(tickers2)
        unique_to_etf1 = tickers1 - tickers2
        unique_to_etf2 = tickers2 - tickers1
        
        # Calculate overlap by weight
        overlap_weight = sum(
            min(holdings1[ticker], holdings2[ticker])
            for ticker in common_tickers
        )
        
        # Build common holdings list (sorted by average weight)
        common_holdings = []
        for ticker in common_tickers:
            weight1 = holdings1[ticker]
            weight2 = holdings2[ticker]
            avg_weight = (weight1 + weight2) / 2
            
            common_holdings.append({
                'symbol': ticker,
                'weight_etf1': weight1,
                'weight_etf1_pct': round(weight1 * 100, 2),
                'weight_etf2': weight2,
                'weight_etf2_pct': round(weight2 * 100, 2),
                'average_weight': avg_weight,
                'average_weight_pct': round(avg_weight * 100, 2),
                'weight_difference': abs(weight1 - weight2),
                'weight_difference_pct': round(abs(weight1 - weight2) * 100, 2)
            })
        
        # Sort by average weight (descending)
        common_holdings.sort(key=lambda x: x['average_weight'], reverse=True)
        
        # Build unique holdings lists
        unique_to_etf1_list = [
            {
                'symbol': ticker,
                'weight': holdings1[ticker],
                'weight_pct': round(holdings1[ticker] * 100, 2)
            }
            for ticker in unique_to_etf1
        ]
        unique_to_etf1_list.sort(key=lambda x: x['weight'], reverse=True)
        
        unique_to_etf2_list = [
            {
                'symbol': ticker,
                'weight': holdings2[ticker],
                'weight_pct': round(holdings2[ticker] * 100, 2)
            }
            for ticker in unique_to_etf2
        ]
        unique_to_etf2_list.sort(key=lambda x: x['weight'], reverse=True)
        
        return {
            'overlap_by_weight': round(overlap_weight, 4),
            'overlap_by_weight_pct': round(overlap_weight * 100, 2),
            'common_count': len(common_tickers),
            'unique_to_etf1_count': len(unique_to_etf1),
            'unique_to_etf2_count': len(unique_to_etf2),
            'common_holdings': common_holdings,
            'unique_to_etf1': unique_to_etf1_list,
            'unique_to_etf2': unique_to_etf2_list
        }
    
    def _calculate_sector_drift(
        self,
        profile1: Dict[str, Any],
        profile2: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Calculate sector allocation differences.
        
        Sector drift shows how sector weightings differ between ETFs.
        Positive drift = ETF1 has more, Negative drift = ETF2 has more
        
        Args:
            profile1: First ETF profile
            profile2: Second ETF profile
            
        Returns:
            List of sector drift data sorted by absolute drift
        """
        # Build sector weight dictionaries
        sectors1 = {s['sector']: s['weight'] for s in profile1.get('sectors', [])}
        sectors2 = {s['sector']: s['weight'] for s in profile2.get('sectors', [])}
        
        # Get all unique sectors
        all_sectors = set(sectors1.keys()).union(set(sectors2.keys()))
        
        # Calculate drift for each sector
        sector_drift = []
        for sector in all_sectors:
            weight1 = sectors1.get(sector, 0.0)
            weight2 = sectors2.get(sector, 0.0)
            drift = weight1 - weight2
            
            sector_drift.append({
                'sector': sector,
                'weight_etf1': weight1,
                'weight_etf1_pct': round(weight1 * 100, 2),
                'weight_etf2': weight2,
                'weight_etf2_pct': round(weight2 * 100, 2),
                'drift': drift,
                'drift_pct': round(drift * 100, 2),
                'absolute_drift': abs(drift),
                'absolute_drift_pct': round(abs(drift) * 100, 2)
            })
        
        # Sort by absolute drift (largest differences first)
        sector_drift.sort(key=lambda x: x['absolute_drift'], reverse=True)
        
        return sector_drift
    
    def _analyze_positions(
        self,
        profile1: Dict[str, Any],
        profile2: Dict[str, Any],
        overlap_data: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Identify overweight and underweight positions.
        
        Overweight = holdings where one ETF has significantly more weight
        than the other (only for common holdings)
        
        Args:
            profile1: First ETF profile
            profile2: Second ETF profile
            overlap_data: Pre-calculated overlap data
            
        Returns:
            Lists of overweight positions for each ETF
        """
        # Find positions where ETF1 is overweight vs ETF2
        overweight_in_etf1 = []
        overweight_in_etf2 = []
        
        for holding in overlap_data['common_holdings']:
            weight_diff = holding['weight_etf1'] - holding['weight_etf2']
            
            # Consider "overweight" if difference > 0.5% (0.005 in decimal)
            if abs(weight_diff) > 0.005:
                position_data = {
                    'symbol': holding['symbol'],
                    'weight_etf1': holding['weight_etf1'],
                    'weight_etf1_pct': holding['weight_etf1_pct'],
                    'weight_etf2': holding['weight_etf2'],
                    'weight_etf2_pct': holding['weight_etf2_pct'],
                    'weight_difference': abs(weight_diff),
                    'weight_difference_pct': round(abs(weight_diff) * 100, 2),
                    'overweight_ratio': round(
                        holding['weight_etf1'] / holding['weight_etf2']
                        if weight_diff > 0 and holding['weight_etf2'] > 0
                        else holding['weight_etf2'] / holding['weight_etf1']
                        if holding['weight_etf1'] > 0
                        else 0,
                        2
                    )
                }
                
                if weight_diff > 0:
                    overweight_in_etf1.append(position_data)
                else:
                    overweight_in_etf2.append(position_data)
        
        # Sort by weight difference (largest first)
        overweight_in_etf1.sort(key=lambda x: x['weight_difference'], reverse=True)
        overweight_in_etf2.sort(key=lambda x: x['weight_difference'], reverse=True)
        
        return {
            'overweight_in_etf1': overweight_in_etf1,
            'overweight_in_etf2': overweight_in_etf2
        }
    
    def _comparison_to_dict(self, comparison: ETFComparison) -> Dict[str, Any]:
        """
        Convert ETFComparison model to dictionary for API response.
        
        Args:
            comparison: ETFComparison model instance
            
        Returns:
            Formatted dictionary with all comparison data
        """
        return {
            'ticker1': comparison.ticker1,
            'ticker2': comparison.ticker2,
            'comparison_summary': {
                'overlap_by_weight': comparison.overlap_by_weight,
                'overlap_by_weight_pct': round(comparison.overlap_by_weight * 100, 2),
                'total_holdings_etf1': comparison.ticker1_stats.get('total_holdings', 0),
                'total_holdings_etf2': comparison.ticker2_stats.get('total_holdings', 0),
                'common_holdings_count': comparison.overlapping_holdings_count,
                'ticker1_in_ticker2_pct': round(comparison.ticker1_in_ticker2_pct * 100, 2),
                'ticker2_in_ticker1_pct': round(comparison.ticker2_in_ticker1_pct * 100, 2)
            },
            'common_holdings': {
                'count': comparison.overlapping_holdings_count,
                'top_20': comparison.overlapping_holdings[:20] if comparison.overlapping_holdings else []
            },
            'sector_drift': [
                {
                    'sector': sector,
                    'drift': drift,
                    'drift_pct': round(drift * 100, 2)
                }
                for sector, drift in sorted(
                    comparison.sector_drift.items(),
                    key=lambda x: abs(x[1]),
                    reverse=True
                )
            ][:10] if comparison.sector_drift else [],
            'overweight_positions': {
                'etf1': comparison.overweight_holdings[:10] if comparison.overweight_holdings else [],
                'etf2': comparison.underweight_holdings[:10] if comparison.underweight_holdings else []
            },
            'metadata': {
                'comparison_date': comparison.comparison_date.isoformat() if comparison.comparison_date else None,
                'fetched_at': comparison.fetched_at.isoformat() if comparison.fetched_at else None
            }
        }


# Singleton instance
etf_comparison_service = ETFComparisonService()
