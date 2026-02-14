"""
ETF Screening Service

Advanced ETF filtering and screening capabilities:
- Filter by sector allocation thresholds
- Filter by fundamentals (expense ratio, AUM, dividend yield)
- Multi-criteria screening
- Sorting and ranking

Phase: 4 of 15
"""

from typing import Dict, List, Optional, Any
from app.core.logging_config import get_logger
from app.repositories.etf_repository import etf_repository

logger = get_logger(__name__)


class ETFScreeningService:
    """
    Service for advanced ETF screening and filtering.
    
    Enables discovery of ETFs matching specific investment criteria.
    """
    
    async def screen_etfs(
        self,
        # Sector filters
        sector: Optional[str] = None,
        min_sector_weight: Optional[float] = None,
        
        # Fundamental filters
        min_assets: Optional[float] = None,
        max_expense_ratio: Optional[float] = None,
        min_dividend_yield: Optional[float] = None,
        
        # Size filters
        min_holdings: Optional[int] = None,
        max_holdings: Optional[int] = None,
        
        # Sorting
        sort_by: str = "net_assets",
        sort_order: str = "desc",
        
        # Pagination
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Screen ETFs based on multiple criteria.
        
        Use Cases:
        - Find large-cap tech ETFs: sector="TECHNOLOGY", min_sector_weight=0.30, min_assets=1B
        - Find low-cost S&P 500 ETFs: max_expense_ratio=0.001, min_holdings=400
        - Find dividend ETFs: min_dividend_yield=0.02
        - Find focused sector ETFs: sector="HEALTHCARE", min_sector_weight=0.80, max_holdings=100
        
        Args:
            sector: Sector name (e.g., "INFORMATION TECHNOLOGY", "FINANCIALS")
            min_sector_weight: Minimum sector allocation (0.0 to 1.0)
                              Example: 0.30 = must have >30% in specified sector
            min_assets: Minimum AUM in dollars
                       Example: 1000000000 = $1 billion minimum
            max_expense_ratio: Maximum expense ratio (0.0 to 1.0)
                              Example: 0.001 = max 0.1% (10 basis points)
            min_dividend_yield: Minimum dividend yield (0.0 to 1.0)
            min_holdings: Minimum number of holdings (focused ETFs have fewer)
            max_holdings: Maximum number of holdings (broad market ETFs have many)
            sort_by: Sort field ("net_assets", "expense_ratio", "total_holdings")
            sort_order: "asc" or "desc"
            limit: Maximum results to return
            
        Returns:
            List of ETFs matching all criteria
            
        Examples:
            >>> # Find large tech ETFs
            >>> result = await screen_etfs(
            ...     sector="INFORMATION TECHNOLOGY",
            ...     min_sector_weight=0.30,
            ...     min_assets=1000000000
            ... )
            
            >>> # Find low-cost S&P 500 ETFs
            >>> result = await screen_etfs(
            ...     max_expense_ratio=0.001,
            ...     min_holdings=400,
            ...     min_assets=10000000000
            ... )
        """
        # Input validation
        if sector is not None and not isinstance(sector, str):
            raise ValueError("sector must be a string")
        
        if min_sector_weight is not None:
            if not isinstance(min_sector_weight, (int, float)):
                raise ValueError("min_sector_weight must be a number")
            if not 0.0 <= min_sector_weight <= 1.0:
                raise ValueError(f"min_sector_weight must be between 0.0 and 1.0, got {min_sector_weight}")
        
        if min_assets is not None:
            if not isinstance(min_assets, (int, float)):
                raise ValueError("min_assets must be a number")
            if min_assets < 0:
                raise ValueError(f"min_assets must be non-negative, got {min_assets}")
        
        if max_expense_ratio is not None:
            if not isinstance(max_expense_ratio, (int, float)):
                raise ValueError("max_expense_ratio must be a number")
            if not 0.0 <= max_expense_ratio <= 1.0:
                raise ValueError(f"max_expense_ratio must be between 0.0 and 1.0, got {max_expense_ratio}")
        
        if min_dividend_yield is not None:
            if not isinstance(min_dividend_yield, (int, float)):
                raise ValueError("min_dividend_yield must be a number")
            if not 0.0 <= min_dividend_yield <= 1.0:
                raise ValueError(f"min_dividend_yield must be between 0.0 and 1.0, got {min_dividend_yield}")
        
        if min_holdings is not None:
            if not isinstance(min_holdings, int):
                raise ValueError("min_holdings must be an integer")
            if min_holdings < 1:
                raise ValueError(f"min_holdings must be at least 1, got {min_holdings}")
        
        if max_holdings is not None:
            if not isinstance(max_holdings, int):
                raise ValueError("max_holdings must be an integer")
            if max_holdings < 1:
                raise ValueError(f"max_holdings must be at least 1, got {max_holdings}")
        
        if min_holdings is not None and max_holdings is not None:
            if min_holdings > max_holdings:
                raise ValueError(f"min_holdings ({min_holdings}) cannot exceed max_holdings ({max_holdings})")
        
        if sort_by not in ["net_assets", "expense_ratio", "total_holdings"]:
            raise ValueError(f"sort_by must be one of: net_assets, expense_ratio, total_holdings. Got: {sort_by}")
        
        if sort_order not in ["asc", "desc"]:
            raise ValueError(f"sort_order must be 'asc' or 'desc'. Got: {sort_order}")
        
        if limit is not None:
            if not isinstance(limit, int):
                raise ValueError("limit must be an integer")
            if limit < 1:
                raise ValueError(f"limit must be at least 1, got {limit}")
            if limit > 10000:
                raise ValueError(f"limit cannot exceed 10000, got {limit}")
        
        logger.info(
            "Screening ETFs",
            extra={
                "sector": sector,
                "min_sector_weight": min_sector_weight,
                "min_assets": min_assets,
                "max_expense_ratio": max_expense_ratio
            }
        )
        
        # Build filters
        filters: Dict[str, Any] = {}
        
        # Get all ETF profiles
        etf_profiles = await etf_repository.get_all_etf_profiles()
        
        if not etf_profiles:
            logger.warning("No ETF profiles found in database")
            return {
                'total_etfs_screened': 0,
                'total_matches': 0,
                'etfs': [],
                'filters_applied': self._build_filter_summary(
                    sector, min_sector_weight, min_assets, max_expense_ratio,
                    min_dividend_yield, min_holdings, max_holdings
                ),
                'note': 'No ETF profiles in database. Fetch some profiles first using /etf/profile/{ticker}'
            }
        
        # Apply filters
        filtered_etfs = []
        
        for etf in etf_profiles:
            # Skip if missing required data
            if not etf.holdings or not etf.sector_allocations:
                continue
            
            # Sector filter
            if sector and min_sector_weight:
                sector_match = False
                sector_upper = sector.upper()
                
                for sector_alloc in etf.sector_allocations:
                    if sector_alloc.get('sector', '').upper() == sector_upper:
                        if sector_alloc.get('weight', 0) >= min_sector_weight:
                            sector_match = True
                            break
                
                if not sector_match:
                    continue
            
            # Assets filter
            if min_assets and (not etf.net_assets or etf.net_assets < min_assets):
                continue
            
            # Expense ratio filter
            if max_expense_ratio and (not etf.net_expense_ratio or etf.net_expense_ratio > max_expense_ratio):
                continue
            
            # Dividend yield filter (if available in future)
            if min_dividend_yield and hasattr(etf, 'dividend_yield'):
                if not etf.dividend_yield or etf.dividend_yield < min_dividend_yield:
                    continue
            
            # Holdings count filters
            if min_holdings and etf.total_holdings < min_holdings:
                continue
            
            if max_holdings and etf.total_holdings > max_holdings:
                continue
            
            # Passed all filters
            filtered_etfs.append(etf)
        
        # Sort results
        reverse = (sort_order.lower() == "desc")
        
        if sort_by == "net_assets":
            filtered_etfs.sort(
                key=lambda e: e.net_assets if e.net_assets else 0,
                reverse=reverse
            )
        elif sort_by == "expense_ratio":
            filtered_etfs.sort(
                key=lambda e: e.net_expense_ratio if e.net_expense_ratio else float('inf'),
                reverse=reverse
            )
        elif sort_by == "total_holdings":
            filtered_etfs.sort(
                key=lambda e: e.total_holdings,
                reverse=reverse
            )
        
        # Apply limit
        if limit:
            filtered_etfs = filtered_etfs[:limit]
        
        # Format results
        results = []
        for etf in filtered_etfs:
            etf_data = {
                'ticker': etf.ticker,
                'name': etf.name,
                'total_holdings': etf.total_holdings,
                'net_assets': etf.net_assets,
                'net_assets_billions': round(etf.net_assets / 1_000_000_000, 2) if etf.net_assets else None,
                'expense_ratio': etf.net_expense_ratio,
                'expense_ratio_pct': round(etf.net_expense_ratio * 100, 4) if etf.net_expense_ratio else None,
                'expense_ratio_bps': round(etf.net_expense_ratio * 10000, 2) if etf.net_expense_ratio else None,
                'sector_allocations': etf.sector_allocations[:5] if etf.sector_allocations else [],
                'top_sectors': self._get_top_sectors(etf.sector_allocations, top_n=3)
            }
            
            # Add sector-specific info if filtering by sector
            if sector and min_sector_weight:
                sector_weight = self._get_sector_weight(etf.sector_allocations, sector)
                if sector_weight:
                    etf_data['sector_allocation'] = {
                        'sector': sector,
                        'weight': sector_weight,
                        'weight_pct': round(sector_weight * 100, 2)
                    }
            
            results.append(etf_data)
        
        logger.info(
            "ETF screening complete",
            extra={
                "total_screened": len(etf_profiles),
                "total_matches": len(results),
                "filters": len([f for f in [sector, min_assets, max_expense_ratio] if f])
            }
        )
        
        return {
            'total_etfs_screened': len(etf_profiles),
            'total_matches': len(results),
            'etfs': results,
            'filters_applied': self._build_filter_summary(
                sector, min_sector_weight, min_assets, max_expense_ratio,
                min_dividend_yield, min_holdings, max_holdings
            ),
            'sorting': {
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        }
    
    async def find_similar_etfs(
        self,
        reference_ticker: str,
        max_expense_ratio_delta: Optional[float] = None,
        max_holdings_delta: Optional[int] = None,
        limit: Optional[int] = 10
    ) -> Dict[str, Any]:
        """
        Find ETFs similar to a reference ETF.
        
        Useful for discovering alternatives to a given ETF.
        
        Args:
            reference_ticker: ETF to compare against (e.g., "SPY")
            max_expense_ratio_delta: Max difference in expense ratio
                                     Example: 0.001 = within 0.1%
            max_holdings_delta: Max difference in holdings count
            limit: Maximum results to return
            
        Returns:
            List of similar ETFs with comparison metrics
        """
        # Get reference ETF
        reference_etf = await etf_repository.get_etf_profile(reference_ticker)
        
        if not reference_etf:
            raise ValueError(f"Reference ETF '{reference_ticker}' not found")
        
        # Get all ETFs
        all_etfs = await etf_repository.get_all_etf_profiles()
        
        similar_etfs = []
        
        for etf in all_etfs:
            # Skip reference ETF itself
            if etf.ticker == reference_ticker:
                continue
            
            # Skip if missing data
            if not etf.holdings or not etf.sector_allocations:
                continue
            
            # Check expense ratio similarity
            if max_expense_ratio_delta and reference_etf.net_expense_ratio and etf.net_expense_ratio:
                expense_delta = abs(etf.net_expense_ratio - reference_etf.net_expense_ratio)
                if expense_delta > max_expense_ratio_delta:
                    continue
            
            # Check holdings count similarity
            if max_holdings_delta:
                holdings_delta = abs(etf.total_holdings - reference_etf.total_holdings)
                if holdings_delta > max_holdings_delta:
                    continue
            
            # Calculate sector overlap
            sector_similarity = self._calculate_sector_similarity(
                reference_etf.sector_allocations,
                etf.sector_allocations
            )
            
            similar_etfs.append({
                'ticker': etf.ticker,
                'name': etf.name,
                'total_holdings': etf.total_holdings,
                'holdings_delta': etf.total_holdings - reference_etf.total_holdings,
                'net_assets': etf.net_assets,
                'net_assets_billions': round(etf.net_assets / 1_000_000_000, 2) if etf.net_assets else None,
                'expense_ratio': etf.net_expense_ratio,
                'expense_ratio_pct': round(etf.net_expense_ratio * 100, 4) if etf.net_expense_ratio else None,
                'expense_ratio_delta': (etf.net_expense_ratio - reference_etf.net_expense_ratio) if (etf.net_expense_ratio and reference_etf.net_expense_ratio) else None,
                'sector_similarity': round(sector_similarity, 4),
                'sector_similarity_pct': round(sector_similarity * 100, 2)
            })
        
        # Sort by sector similarity (descending)
        similar_etfs.sort(key=lambda e: e['sector_similarity'], reverse=True)
        
        # Apply limit
        if limit:
            similar_etfs = similar_etfs[:limit]
        
        return {
            'reference_ticker': reference_ticker,
            'reference_etf': {
                'ticker': reference_etf.ticker,
                'name': reference_etf.name,
                'total_holdings': reference_etf.total_holdings,
                'net_assets': reference_etf.net_assets,
                'expense_ratio': reference_etf.net_expense_ratio
            },
            'total_similar_found': len(similar_etfs),
            'similar_etfs': similar_etfs,
            'filters_applied': {
                'max_expense_ratio_delta': max_expense_ratio_delta,
                'max_holdings_delta': max_holdings_delta,
                'limit': limit
            }
        }
    
    def _get_sector_weight(
        self,
        sector_allocations: List[Dict],
        sector_name: str
    ) -> Optional[float]:
        """Get weight for a specific sector."""
        sector_upper = sector_name.upper()
        for sector_alloc in sector_allocations:
            if sector_alloc.get('sector', '').upper() == sector_upper:
                return sector_alloc.get('weight')
        return None
    
    def _get_top_sectors(
        self,
        sector_allocations: List[Dict],
        top_n: int = 3
    ) -> List[Dict]:
        """Get top N sectors by weight."""
        if not sector_allocations:
            return []
        
        sorted_sectors = sorted(
            sector_allocations,
            key=lambda s: s.get('weight', 0),
            reverse=True
        )
        
        return [
            {
                'sector': s.get('sector'),
                'weight': s.get('weight'),
                'weight_pct': round(s.get('weight', 0) * 100, 2)
            }
            for s in sorted_sectors[:top_n]
        ]
    
    def _calculate_sector_similarity(
        self,
        sectors1: List[Dict],
        sectors2: List[Dict]
    ) -> float:
        """
        Calculate sector allocation similarity.
        
        Uses inverse of sum of absolute differences (1 - SAD).
        Returns value between 0 (completely different) and 1 (identical).
        """
        # Build sector weight dictionaries
        sectors1_dict = {s.get('sector'): s.get('weight', 0) for s in sectors1}
        sectors2_dict = {s.get('sector'): s.get('weight', 0) for s in sectors2}
        
        # Get all unique sectors
        all_sectors = set(sectors1_dict.keys()).union(sectors2_dict.keys())
        
        # Calculate sum of absolute differences
        sad = sum(
            abs(sectors1_dict.get(sector, 0) - sectors2_dict.get(sector, 0))
            for sector in all_sectors
        )
        
        # Similarity = 1 - (SAD / 2)
        # Divide by 2 because SAD ranges from 0 to 2
        similarity = 1 - (sad / 2)
        
        return max(0, similarity)  # Ensure non-negative
    
    def _build_filter_summary(
        self,
        sector: Optional[str],
        min_sector_weight: Optional[float],
        min_assets: Optional[float],
        max_expense_ratio: Optional[float],
        min_dividend_yield: Optional[float],
        min_holdings: Optional[int],
        max_holdings: Optional[int]
    ) -> Dict[str, Any]:
        """Build human-readable filter summary."""
        summary = {}
        
        if sector and min_sector_weight:
            summary['sector'] = {
                'sector_name': sector,
                'min_weight': min_sector_weight,
                'min_weight_pct': round(min_sector_weight * 100, 2),
                'description': f"{sector} allocation >= {round(min_sector_weight * 100, 2)}%"
            }
        
        if min_assets:
            summary['min_assets'] = {
                'value': min_assets,
                'billions': round(min_assets / 1_000_000_000, 2),
                'description': f"AUM >= ${round(min_assets / 1_000_000_000, 2)}B"
            }
        
        if max_expense_ratio:
            summary['max_expense_ratio'] = {
                'value': max_expense_ratio,
                'pct': round(max_expense_ratio * 100, 4),
                'bps': round(max_expense_ratio * 10000, 2),
                'description': f"Expense ratio <= {round(max_expense_ratio * 100, 4)}% ({round(max_expense_ratio * 10000, 2)} bps)"
            }
        
        if min_dividend_yield:
            summary['min_dividend_yield'] = {
                'value': min_dividend_yield,
                'pct': round(min_dividend_yield * 100, 2),
                'description': f"Dividend yield >= {round(min_dividend_yield * 100, 2)}%"
            }
        
        if min_holdings:
            summary['min_holdings'] = {
                'value': min_holdings,
                'description': f"Holdings >= {min_holdings}"
            }
        
        if max_holdings:
            summary['max_holdings'] = {
                'value': max_holdings,
                'description': f"Holdings <= {max_holdings}"
            }
        
        return summary


# Singleton instance
etf_screening_service = ETFScreeningService()
