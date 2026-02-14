"""
Run Cartographer to scrape FinViz data for a ticker.

Usage:
    python3 run_cartographer.py [TICKER]
    
Example:
    python3 run_cartographer.py NVDA
"""

import sys
import asyncio
import json
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.cartographer.scanner import CartographerScanner


async def main():
    ticker = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
    
    print(f"🚀 Starting Cartographer for {ticker}")
    print("=" * 60)
    
    scanner = CartographerScanner()
    
    # Scrape FinViz
    result = await scanner.scrape_finviz(ticker)
    
    if result:
        print(f"\n✅ Successfully scraped {ticker} from FinViz")
        print("=" * 60)
        
        # Pretty print the result
        print(json.dumps(result, indent=2, default=str))
        
        # Save to file
        output_file = f"cartographer_output_{ticker.lower()}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"\n💾 Saved to: {output_file}")
    else:
        print(f"\n❌ Failed to scrape {ticker}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
