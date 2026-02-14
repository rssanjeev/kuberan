#!/usr/bin/env python3
"""
Run Cartographer Scanner

Tests the Cartographer architecture by scanning FinViz and generating a site dictionary.

Usage:
    python3 run_cartographer_scanner.py
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.services.cartographer.scanner import CartographerScanner
from app.core.logging_config import get_logger

logger = get_logger(__name__)


async def main():
    """Run the Cartographer scanner on FinViz test config."""
    
    # Config path
    config_path = backend_path / "app/services/cartographer/configs/finviz_test.yaml"
    
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        return
    
    logger.info("=" * 80)
    logger.info("🗺️  CARTOGRAPHER SCANNER TEST")
    logger.info("=" * 80)
    logger.info(f"Config: {config_path}")
    logger.info(f"Target: FinViz quote pages")
    logger.info("")
    
    # Initialize scanner
    scanner = CartographerScanner(config_path)
    
    # Sample URLs to test
    test_urls = [
        "https://finviz.com/quote.ashx?t=NVDA",  # Stock
        "https://finviz.com/quote.ashx?t=AAPL",  # Stock
        "https://finviz.com/quote.ashx?t=VOO",   # ETF
    ]
    
    logger.info(f"Test URLs: {len(test_urls)}")
    for url in test_urls:
        logger.info(f"  - {url}")
    logger.info("")
    
    try:
        # Run scanner
        logger.info("Starting scanner...")
        site_dict = await scanner.scan(test_urls)
        
        logger.info("")
        logger.info("✅ Scan complete!")
        logger.info("")
        
        # Display results
        logger.info("Site Dictionary Generated:")
        logger.info(f"  Site: {site_dict.site_name}")
        logger.info(f"  Generated: {site_dict.generated_at}")
        logger.info(f"  Templates: {len(site_dict.templates)}")
        logger.info(f"  Interceptors: {len(site_dict.interceptors)}")
        logger.info("")
        
        for template_name, template in site_dict.templates.items():
            logger.info(f"Template: {template_name}")
            logger.info(f"  Signature: {template.signature.name}")
            logger.info(f"  Regions: {len(template.regions)}")
            for region in template.regions:
                logger.info(f"    - {region.region_id}: {len(region.parsing_rules)} rules")
        
        # Save to JSON
        output_path = backend_path / "app/services/cartographer/configs/finviz_site_dictionary.json"
        
        logger.info("")
        logger.info(f"Saving site dictionary to: {output_path}")
        
        with open(output_path, 'w') as f:
            json.dump(site_dict.dict(), f, indent=2, default=str)
        
        logger.info("✅ Site dictionary saved!")
        logger.info("")
        logger.info("=" * 80)
        logger.info("🎉 CARTOGRAPHER SCANNER TEST COMPLETE!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Scanner failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
