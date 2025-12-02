"""
Service for ticker type operations.

Business logic for fetching, storing, and querying ticker type reference data
from MASSIVE API (CS, ETF, ADRC, PFD, etc.).
"""

from typing import List, Optional

from app.services.providers.implementations.massive_provider import MassiveProvider
from app.repositories.ticker_type_repository import ticker_type_repository
from app.models.stock import TickerType
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class TickerTypeService:
    """Service for ticker type operations."""

    async def fetch_and_store_types(
        self,
        provider: MassiveProvider,
        asset_class: Optional[str] = None,
        locale: Optional[str] = None
    ) -> int:
        """
        Fetch ticker types from MASSIVE API and store in database.

        Args:
            provider: MASSIVE provider instance
            asset_class: Filter by asset class (default: stocks)
            locale: Filter by locale (default: us)

        Returns:
            Count of ticker types stored

        Raises:
            ProviderException: If API call fails
        """
        logger.info(
            "Fetching ticker types from MASSIVE",
            extra={"asset_class": asset_class, "locale": locale}
        )

        # Fetch from API
        types = await provider.fetch_ticker_types(
            asset_class=asset_class or "stocks",
            locale=locale or "us"
        )

        if not types:
            logger.warning("No ticker types returned from MASSIVE")
            return 0

        # Store in database
        count = await ticker_type_repository.save_ticker_types(types)

        logger.info(
            "Successfully stored ticker types",
            extra={"count": count}
        )

        return count

    async def get_types(
        self,
        asset_class: Optional[str] = None,
        locale: Optional[str] = None
    ) -> List[TickerType]:
        """
        Get ticker types from database with optional filters.

        Args:
            asset_class: Filter by asset class (stocks, options, crypto, fx, indices)
            locale: Filter by locale (us, global)

        Returns:
            List of TickerType documents
        """
        logger.debug(
            "Retrieving ticker types",
            extra={"asset_class": asset_class, "locale": locale}
        )

        types = await ticker_type_repository.get_all(
            asset_class=asset_class,
            locale=locale
        )

        logger.info(
            "Retrieved ticker types",
            extra={"count": len(types)}
        )

        return types

    async def get_by_code(self, code: str) -> Optional[TickerType]:
        """
        Get specific ticker type by code.

        Args:
            code: Ticker type code (CS, ETF, ADRC, etc.)

        Returns:
            TickerType document or None if not found
        """
        logger.debug(
            "Retrieving ticker type by code",
            extra={"code": code}
        )

        ticker_type = await ticker_type_repository.get_by_code(code)

        if ticker_type:
            logger.info(
                "Found ticker type",
                extra={"code": code, "description": ticker_type.description}
            )
        else:
            logger.warning(
                "Ticker type not found",
                extra={"code": code}
            )

        return ticker_type

    async def get_count(self) -> int:
        """
        Get total count of ticker types in database.

        Returns:
            Total count
        """
        count = await ticker_type_repository.count()

        logger.debug(
            "Ticker type count",
            extra={"count": count}
        )

        return count


# Singleton instance
ticker_type_service = TickerTypeService()
