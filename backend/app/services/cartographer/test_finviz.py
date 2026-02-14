"""
Cartographer Test Script - FinViz Validation

Last Updated: 2025-12-20
Purpose: Test Cartographer scanner and parser with FinViz

Usage:
    cd backend
    python3 -m app.services.cartographer.test_finviz

Expected Output:
1. Load finviz.yaml configuration
2. Scan FinViz quote page (AAPL)
3. Generate site dictionary JSON
4. Parse NVDA quote page using dictionary
5. Display extracted data
"""

import asyncio
from pathlib import Path

from app.services.cartographer import CartographerScanner, SmartParser
from app.core.logging_config import get_logger

logger = get_logger(__name__)


async def main():
    """Test Cartographer with FinViz."""
    
    print("\n" + "="*70)
    print("CARTOGRAPHER TEST - FINVIZ QUOTE PAGE")
    print("="*70 + "\n")

    # Paths
    config_path = Path("config/cartographer/template_definitions/finviz.yaml")
    dict_path = Path("config/cartographer/site_dictionaries/finviz_dictionary.json")

    # Sample URLs for testing
    sample_urls = {
        "quote_page": "https://finviz.com/quote.ashx?t=AAPL&p=d"
    }

    # Step 1: Initialize Scanner
    print("Step 1: Initialize Cartographer Scanner")
    print("-" * 70)
    scanner = CartographerScanner(config_path)
    await scanner.load_config()
    print(f"✓ Configuration loaded: {scanner.site_name}\n")

    # Step 2: Scan Site
    print("Step 2: Scan FinViz Quote Page (AAPL)")
    print("-" * 70)
    print("→ Launching browser...")
    print("→ Navigating to https://finviz.com/quote.ashx?t=AAPL&p=d")
    print("→ Validating selectors (primary + fallbacks)...")
    
    try:
        dictionary = await scanner.scan_site(sample_urls)
        print(f"✓ Site scan complete")
        print(f"  - Templates validated: {len(dictionary.templates)}")
        
        # Show validated regions
        if dictionary.templates:
            template = dictionary.templates[0]
            print(f"  - Regions found: {len(template['regions'])}")
            for region in template["regions"]:
                valid_count = sum(1 for rule in region["parsing_rules"] if rule.get("valid", False))
                total_count = len(region["parsing_rules"])
                print(f"    • {region['region_id']}: {valid_count}/{total_count} fields valid")
        
        print()

        # Step 3: Save Dictionary
        print("Step 3: Save Site Dictionary")
        print("-" * 70)
        await scanner.save_dictionary(dictionary, dict_path)
        print(f"✓ Dictionary saved: {dict_path}\n")

    except Exception as e:
        print(f"✗ Scan failed: {e}\n")
        logger.error("Scan failed", extra={"error": str(e)}, exc_info=True)
        return

    # Step 4: Initialize Parser
    print("Step 4: Initialize Smart Parser")
    print("-" * 70)
    parser = SmartParser(dict_path)
    parser.load_dictionary()
    print(f"✓ Dictionary loaded: {parser.dictionary.site_name}\n")

    # Step 5: Extract Data
    print("Step 5: Extract Data from NVDA Quote Page")
    print("-" * 70)
    print("→ Launching browser...")
    print("→ Navigating to https://finviz.com/quote.ashx?t=NVDA&p=d")
    print("→ Extracting fields...")
    
    try:
        test_url = "https://finviz.com/quote.ashx?t=NVDA&p=d"
        data = await parser.extract_data(test_url)
        
        print(f"✓ Data extraction complete\n")
        
        # Display extracted data by region
        print("EXTRACTED DATA:")
        print("-" * 70)
        
        for region_id, region_data in data["regions"].items():
            print(f"\n{region_id.upper()}:")
            for field, value in region_data.items():
                if value is not None:
                    print(f"  {field}: {value}")
                else:
                    print(f"  {field}: (not found)")
        
        print()

        await parser.close()

    except Exception as e:
        print(f"✗ Extraction failed: {e}\n")
        logger.error("Extraction failed", extra={"error": str(e)}, exc_info=True)
        return

    # Summary
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print("\nNext Steps:")
    print("1. Review extracted data above")
    print("2. Check logs for selector failures")
    print("3. Update finviz.yaml if selectors need adjustment")
    print("4. Re-run scanner to regenerate dictionary")
    print()


if __name__ == "__main__":
    asyncio.run(main())
