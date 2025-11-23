"""
ETF Discovery Service

Provides stock-to-ETF lookup functionality:
- Find all ETFs holding a specific stock
- Filter by minimum weight threshold
- Sort by holding weight
- Search capabilities

Phase: 3 of 15
"""

from typing import Dict, List, Optional, Any
from app.core.logging_config import get_logger
from app.repositories.etf_repository import etf_repository

logger = get_logger(__name__)


class ETFDiscoveryService:
    """
    Service for discovering ETFs based on holdings.
    
    Primary use case: "Which ETFs hold AAPL?"
    """
    
    async def find_etfs_holding_stock(
        self,
        stock_symbol: str,
        min_weight: Optional[float] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Find all ETFs that hold a specific stock.
        
        Use Cases:
        - Find which ETFs have exposure to NVDA
        - Find ETFs with >5% allocation to AAPL
        - Discover sector ETFs vs broad market ETFs
        
        Args:
            stock_symbol: Stock ticker symbol (e.g., "AAPL", "NVDA")
            min_weight: Minimum weight threshold (0.0 to 1.0)
                       Example: 0.05 = only ETFs with >5% allocation
            limit: Maximum number of results to return
            
        Returns:
            List of ETFs holding the stock, sorted by weight (descending)
            
        Example:
            >>> result = await find_etfs_holding_stock("AAPL", min_weight=0.05)
            >>> print(result['etfs'][0])
            {
                "ticker": "QQQ",
                "name": "Invesco QQQ Trust",
                "weight": 0.0871,
                "weight_pct": 8.71,
                "rank": 2  # AAPL is 2nd largest holding in QQQ
            }
        """
        stock_symbol = stock_symbol.upper().strip()
        
        logger.info(
            "Searching for ETFs holding stock",
            extra={"stock_symbol": stock_symbol, "min_weight": min_weight}
        )
        
        # Search database for ETFs containing this stock
        etf_profiles = await etf_repository.search_etfs_by_stock(
            symbol=stock_symbol,
            min_weight=min_weight
        )
        
        if not etf_profiles:
            logger.info(
                "No ETFs found holding stock",
                extra={"stock_symbol": stock_symbol, "min_weight": min_weight}
            )
            return {
                'stock_symbol': stock_symbol,
                'total_etfs_found': 0,
                'etfs': [],
                'note': 'No ETFs found. This could mean: 1) Stock not held by any ETF in database, 2) Weight below threshold, 3) ETF data not yet fetched.'
            }
        
        # Extract holding information for each ETF
        etfs_with_holdings = []
        for etf in etf_profiles:
            # Find the specific holding in this ETF
            holding_info = None
            holding_rank = None
            
            for idx, holding in enumerate(etf.holdings, start=1):
                if holding.get('symbol') == stock_symbol:
                    weight = holding.get('weight', 0.0)
                    holding_info = {
                        'ticker': etf.ticker,
                        'name': etf.name,
                        'weight': weight,
                        'weight_pct': round(weight * 100, 2),
                        'rank': idx,  # Position in holdings list (1 = largest)
                        'description': holding.get('description'),
                        'total_holdings': etf.total_holdings,
                        'net_assets': etf.net_assets,
                        'expense_ratio': etf.net_expense_ratio,
                        'expense_ratio_pct': round(etf.net_expense_ratio * 100, 4) if etf.net_expense_ratio else None
                    }
                    holding_rank = idx
                    break
            
            if holding_info:
                etfs_with_holdings.append(holding_info)
        
        # Sort by weight (descending - highest exposure first)
        etfs_with_holdings.sort(key=lambda x: x['weight'], reverse=True)
        
        # Apply limit if specified
        if limit:
            etfs_with_holdings = etfs_with_holdings[:limit]
        
        # Calculate statistics
        total_weight = sum(etf['weight'] for etf in etfs_with_holdings)
        avg_weight = total_weight / len(etfs_with_holdings) if etfs_with_holdings else 0
        
        top_etf = etfs_with_holdings[0] if etfs_with_holdings else None
        
        logger.info(
            "Found ETFs holding stock",
            extra={
                "stock_symbol": stock_symbol,
                "total_etfs": len(etfs_with_holdings),
                "avg_weight": avg_weight,
                "top_etf": top_etf['ticker'] if top_etf else None
            }
        )
        
        return {
            'stock_symbol': stock_symbol,
            'total_etfs_found': len(etfs_with_holdings),
            'statistics': {
                'average_weight': round(avg_weight, 4),
                'average_weight_pct': round(avg_weight * 100, 2),
                'total_combined_weight': round(total_weight, 4),
                'highest_weight_etf': top_etf['ticker'] if top_etf else None,
                'highest_weight': top_etf['weight'] if top_etf else None,
                'highest_weight_pct': top_etf['weight_pct'] if top_etf else None
            },
            'etfs': etfs_with_holdings,
            'filters_applied': {
                'min_weight': min_weight,
                'min_weight_pct': round(min_weight * 100, 2) if min_weight else None,
                'limit': limit
            }
        }
    
    async def get_stock_exposure_summary(
        self,
        stock_symbol: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive exposure summary for a stock across all ETFs.
        
        Provides insights like:
        - Which sector ETFs hold this stock
        - Broad market vs niche ETF exposure
        - Largest and smallest holders
        
        Args:
            stock_symbol: Stock ticker symbol
            
        Returns:
            Exposure summary with categorization
        """
        stock_symbol = stock_symbol.upper().strip()
        
        # Get all ETFs holding this stock
        result = await self.find_etfs_holding_stock(stock_symbol)
        
        if result['total_etfs_found'] == 0:
            return result
        
        etfs = result['etfs']
        
        # Categorize ETFs by weight
        heavy_holders = [e for e in etfs if e['weight'] >= 0.05]  # >5%
        moderate_holders = [e for e in etfs if 0.01 <= e['weight'] < 0.05]  # 1-5%
        light_holders = [e for e in etfs if e['weight'] < 0.01]  # <1%
        
        # Find top position holders (stock in top 10)
        top_10_holders = [e for e in etfs if e['rank'] <= 10]
        
        return {
            'stock_symbol': stock_symbol,
            'total_etfs_found': result['total_etfs_found'],
            'statistics': result['statistics'],
            'exposure_breakdown': {
                'heavy_holders': {
                    'count': len(heavy_holders),
                    'description': 'ETFs with >5% allocation',
                    'etfs': heavy_holders[:10]  # Top 10
                },
                'moderate_holders': {
                    'count': len(moderate_holders),
                    'description': 'ETFs with 1-5% allocation',
                    'etfs': moderate_holders[:10]
                },
                'light_holders': {
                    'count': len(light_holders),
                    'description': 'ETFs with <1% allocation',
                    'etfs': light_holders[:10]
                },
                'top_10_positions': {
                    'count': len(top_10_holders),
                    'description': 'ETFs where stock is in top 10 holdings',
                    'etfs': top_10_holders[:10]
                }
            },
            'top_holders': etfs[:5],  # Top 5 by weight
            'filters_applied': result['filters_applied']
        }


# Singleton instance
etf_discovery_service = ETFDiscoveryService()
