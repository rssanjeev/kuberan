#!/usr/bin/env python3
"""
Run Cartographer Scanner - Scan FinViz and Generate Site Dictionary

This script demonstrates the Cartographer architecture:
1. Load YAML configuration for FinViz
2. Launch Playwright browser
3. Navigate to sample pages
4. Validate selectors and generate site dictionary
5. Save results to JSON

Usage:
    python3 scripts/run_cartographer.py
    
    # Or with a specific ticker:
    python3 scripts/run_cartographer.py AAPL
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.cartographer.scanner import CartographerScanner


async def main(ticker: str = "NVDA"):
    """Run Cartographer scanner on FinViz."""
    
    print(f"\n{'='*60}")
    print("🗺️  CARTOGRAPHER SCANNER")
    print(f"{'='*60}")
    print(f"Target: FinViz Quote Page")
    print(f"Ticker: {ticker}")
    print(f"{'='*60}\n")
    
    # Config path
    config_path = Path(__file__).parent.parent / "backend/app/services/cartographer/configs/finviz_test.yaml"
    
    if not config_path.exists():
        print(f"❌ Config not found: {config_path}")
        return
    
    print(f"📄 Loading config: {config_path.name}")
    
    # Initialize scanner
    scanner = CartographerScanner(config_path)
    
    # Define sample URLs for each template
    sample_urls = {
        "stock_page": f"https://finviz.com/quote.ashx?t={ticker}&p=d"
    }
    
    print(f"🌐 Sample URL: {sample_urls['stock_page']}")
    print()
    
    try:
        # Scan site
        print("🔍 Starting scan...")
        print("   - Launching browser (headless)")
        print("   - Navigating to page")
        print("   - Validating selectors")
        print()
        
        dictionary = await scanner.scan_site(sample_urls)
        
        print(f"\n{'='*60}")
        print("✅ SCAN COMPLETE")
        print(f"{'='*60}")
        print(f"Site: {dictionary.site_name}")
        print(f"Base URL: {dictionary.base_url}")
        print(f"Templates validated: {len(dictionary.templates)}")
        print()
        
        # Show results - templates is Dict[str, PageTemplate]
        for template_name, template in dictionary.templates.items():
            print(f"📋 Template: {template_name}")
            print(f"   URL Pattern: {template.signature.url_pattern}")
            print(f"   Regions: {len(template.regions)}")
            print()
            
            for region in template.regions:
                print(f"   📦 Region: {region.region_id}")
                print(f"      Container: {region.container_selector}")
                print(f"      Fields: {len(region.parsing_rules)}")
                
                for rule in region.parsing_rules:
                    selector_text = rule.selector.primary[:60]
                    print(f"      • {rule.field_name}: {selector_text}...")
                print()
        
        # Save dictionary
        output_path = Path(__file__).parent.parent / "backend/app/services/cartographer/configs/finviz_dictionary.json"
        await scanner.save_dictionary(dictionary, output_path)
        print(f"💾 Dictionary saved: {output_path}")
        
    except Exception as e:
        print(f"\n❌ Scan failed: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    # Get ticker from command line or use default
    ticker = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
    
    asyncio.run(main(ticker))
