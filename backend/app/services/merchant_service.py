    """
Merchant Service - Merchant and Category Management

Provides CRUD operations for merchant-category mappings.
"""

from typing import Dict, Any
from app.repositories.financial_repository import merchant_category_repository


class MerchantService:
    """Service for managing merchants and category mappings."""
    
    async def get_all_merchants(self) -> Dict[str, Any]:
        """
        Get all merchants with their category mappings.
        
        Returns:
            List of merchants with categories
        """
        mappings = await merchant_category_repository.get_all_merchants()
        
        return {
            "count": len(mappings),
            "merchants": [
                {
                    "merchant": m.merchant_name,
                    "category": m.category,
                    "source": m.source,
                    "confidence": m.confidence,
                    "last_updated": m.updated_at.isoformat()
                }
                for m in mappings
            ]
        }
    
    async def get_merchants_by_category(self, category: str) -> Dict[str, Any]:
        """
        Get all merchants in a specific category.
        
        Args:
            category: Category name
            
        Returns:
            List of merchants in that category
        """
        mappings = await merchant_category_repository.get_merchants_by_category(category)
        
        return {
            "category": category,
            "count": len(mappings),
            "merchants": [
                {
                    "merchant": m.merchant_name,
                    "source": m.source,
                    "confidence": m.confidence,
                    "last_updated": m.updated_at.isoformat()
                }
                for m in mappings
            ]
        }
    
    async def update_merchant_category(
        self,
        merchant_name: str,
        new_category: str
    ) -> Dict[str, Any]:
        """
        Reassign a merchant to a different category.
        Updates both the merchant mapping and all related transactions.
        
        Args:
            merchant_name: Merchant name
            new_category: New category to assign
            
        Returns:
            Update result
        """
        mapping = await merchant_category_repository.update_merchant_category(
            merchant_name=merchant_name,
            new_category=new_category,
            source="manual"
        )
        
        if not mapping:
            raise ValueError(f"Merchant '{merchant_name}' not found")
        
        return {
            "status": "success",
            "message": f"Merchant '{merchant_name}' reassigned to '{new_category}'",
            "merchant": merchant_name,
            "old_category": mapping.category if mapping else None,
            "new_category": new_category
        }
    
    async def add_custom_category(self, category_name: str) -> Dict[str, Any]:
        """
        Add a new custom category.
        
        Args:
            category_name: Name of the new category
            
        Returns:
            Status result
        """
        return await merchant_category_repository.add_custom_category(category_name)


# Singleton instance
merchant_service = MerchantService()
