"""
Repository for ticker type reference data.

Handles database operations for MASSIVE ticker type classifications.
Types are reference data (CS, ETF, ADRC, etc.) fetched once and cached permanently.
"""

from typing import List, Optional
from datetime import datetime

from app.models.stock import TickerType
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class TickerTypeRepository:
    """Repository for ticker type reference data."""

    async def save_ticker_types(self, types: List[dict]) -> int:
        """
        Save ticker types to database.

        Args:
            types: List of ticker type dictionaries from MASSIVE API

        Returns:
            Count of ticker types saved

        Example:
            types = [
                {"code": "CS", "description": "Common Stock", "asset_class": "stocks", "locale": "us"},
                {"code": "ETF", "description": "Exchange Traded Fund", "asset_class": "stocks", "locale": "us"}
            ]
            count = await ticker_type_repository.save_ticker_types(types)
        """
        count = 0

        for type_data in types:
            # Check if already exists (based on code)
            existing = await TickerType.find_one({"code": type_data["code"]})

            if existing:
                # Update existing
                existing.description = type_data["description"]
                existing.asset_class = type_data["asset_class"]
                existing.locale = type_data["locale"]
                existing.fetched_at = datetime.utcnow()
                await existing.save()

                logger.debug(
                    "Updated existing ticker type",
                    extra={"code": type_data["code"]}
                )
            else:
                # Create new
                ticker_type = TickerType(
                    code=type_data["code"],
                    description=type_data["description"],
                    asset_class=type_data["asset_class"],
                    locale=type_data["locale"],
                    fetched_at=datetime.utcnow()
                )
                await ticker_type.insert()

                logger.debug(
                    "Created new ticker type",
                    extra={"code": type_data["code"]}
                )

            count += 1

        logger.info(
            "Saved ticker types to database",
            extra={"count": count}
        )

        return count

    async def get_all(
        self,
        asset_class: Optional[str] = None,
        locale: Optional[str] = None
    ) -> List[TickerType]:
        """
        Get all ticker types with optional filters.

        Args:
            asset_class: Filter by asset class (stocks, options, crypto, fx, indices)
            locale: Filter by locale (us, global)

        Returns:
            List of TickerType documents
        """
        query = TickerType.find()

        if asset_class:
            query = TickerType.find({"asset_class": asset_class})

        if locale:
            # If both filters, need to combine
            if asset_class:
                query = TickerType.find({"asset_class": asset_class, "locale": locale})
            else:
                query = TickerType.find({"locale": locale})

        types = await query.to_list()

        logger.debug(
            "Retrieved ticker types from database",
            extra={
                "count": len(types),
                "asset_class": asset_class,
                "locale": locale
            }
        )

        return types

    async def get_by_code(self, code: str) -> Optional[TickerType]:
        """
        Get ticker type by code.

        Args:
            code: Ticker type code (CS, ETF, ADRC, etc.)

        Returns:
            TickerType document or None if not found
        """
        ticker_type = await TickerType.find_one({"code": code})

        if ticker_type:
            logger.debug(
                "Retrieved ticker type by code",
                extra={"code": code}
            )
        else:
            logger.debug(
                "Ticker type not found",
                extra={"code": code}
            )

        return ticker_type

    async def count(self) -> int:
        """
        Count total ticker types in database.

        Returns:
            Total count
        """
        count = await TickerType.find_all().count()

        logger.debug(
            "Counted ticker types",
            extra={"count": count}
        )

        return count


# Singleton instance
ticker_type_repository = TickerTypeRepository()
