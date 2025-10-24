# Project Context: Kuberan Investment Projection Tool

## Project Overview
**Kuberan** is a Python-based investment projection tool that analyzes dividend-paying stocks/ETFs and projects portfolio growth over time using different investment strategies with dividend reinvestment (DRIP).

## What This Tool Does
- **Scrapes financial data** from StockAnalysis.com and Yahoo Finance
- **Models different investment strategies** (Safe, Moderate, Growth, Aggressive)
- **Projects quarterly growth** over 3 years with dividend reinvestment
- **Generates detailed CSV reports** showing portfolio evolution

## Project Evolution

### Phase 1: Initial Script (Completed)
- Started as a single monolithic `main.py` script
- Hardcoded investment strategies and configuration
- Basic web scraping for stock data
- Simple CSV output generation

### Phase 2: Configuration Externalization (Completed)
- Moved strategies to `.env` file for external configuration
- Added python-dotenv for environment variable management
- Made ticker symbols and quarters configurable

### Phase 3: Object-Oriented Refactor (Completed - October 2025)
**Major architectural transformation:**
- **Converted to OOP design** with proper separation of concerns
- **Created modular structure** with models and services packages
- **Implemented proper error handling** and type hints
- **Added comprehensive documentation**

## Current Architecture

### Models Package (`models/`)
- **`Config`**: Environment variable management and strategy loading
- **`StockData`**: Data class for stock financial information
- **`InvestmentStrategy`**: Data class for investment strategy configuration
- **`PortfolioProjector`**: Core projection calculation logic

### Services Package (`services/`)
- **`StockDataScraper`**: Abstract base class for scrapers
- **`StockAnalysisScraper`**: StockAnalysis.com data scraper
- **`YahooFinanceScraper`**: Yahoo Finance data scraper
- **`StockDataService`**: Orchestrates data retrieval with fallbacks
- **`ReportService`**: CSV report generation

### Application Layer
- **`InvestmentProjectionApp`**: Main application orchestrator
- **`main.py`**: Simple entry point

## Key Features Implemented
- ✅ **Multiple data sources** with automatic fallback
- ✅ **Configurable investment strategies** via .env file
- ✅ **Manual data overrides** for specific tickers (e.g., VXUS)
- ✅ **Quarterly dividend reinvestment** with growth modeling
- ✅ **Comprehensive error handling** and logging
- ✅ **Type hints** throughout codebase
- ✅ **CSV report generation** with detailed projections

## Technical Details

### Data Sources
1. **StockAnalysis.com** (primary)
2. **Yahoo Finance** (fallback)
3. **Manual overrides** for specific tickers

### Investment Strategies (configurable via .env)
- **Safe**: $1,000 initial + $100/month
- **Moderate**: $2,500 initial + $200/month  
- **Growth**: $3,500 initial + $350/month
- **Aggressive**: $5,000 initial + $500/month

### Projection Logic
- **Time horizon**: 12 quarters (3 years) - configurable
- **Dividend frequency**: Quarterly payments
- **Growth modeling**: Compound quarterly growth
- **Reinvestment**: Automatic dividend reinvestment (DRIP)

## Known Issues & Solutions
1. **urllib3 SSL warning**: LibreSSL compatibility issue (non-blocking)
2. **Web scraping reliability**: Implemented fallback scrapers and manual overrides
3. **VXUS price fix**: Manual override with correct $74.97 price vs incorrect scraped $6,730

## Dependencies
- `requests`: HTTP requests for web scraping
- `beautifulsoup4`: HTML parsing
- `python-dotenv`: Environment variable management

## Configuration (.env file)
```env
QUARTERS=12
TICKER=VXUS
STRATEGY_1=Safe:1000:100
STRATEGY_2=Moderate:2500:200
STRATEGY_3=Growth:3500:350
STRATEGY_4=Aggressive:5000:500
```

## Output Format
CSV files saved to `Reports/Projections/{TICKER}_projection.csv` with columns:
- Strategy, Quarter, Initial_Investment, Quarterly_Investment
- Total Shares, Total_Investment, Projected_Balance

## Development Context for Future Reference

### Code Quality Standards
- **Type hints** throughout codebase
- **Docstrings** for all classes and methods
- **Error handling** with specific exceptions
- **Modular design** with clear separation of concerns

### Testing Considerations
- Web scraping components are mockable
- Configuration is externalized for test environments
- Pure calculation logic is isolated in projection classes

### Future Enhancement Areas
1. **Additional data sources** (Alpha Vantage, IEX Cloud)
2. **More investment strategies** and custom strategy builder
3. **Web interface** or CLI improvements
4. **Database persistence** for historical tracking
5. **Visualization** of projections (charts, graphs)
6. **Portfolio optimization** algorithms
7. **Risk analysis** and Monte Carlo simulations

### Branch Status
- **Current branch**: `initital-setup` (note: typo in branch name)
- **Default branch**: `develop`
- Ready for merge after testing

## Usage Examples
```bash
# Run with default ticker (VXUS)
python main.py

# Run with specific ticker
python main.py SCHD

# Output: Reports/Projections/{TICKER}_projection.csv
```

---
*Last updated: October 24, 2025*
*Next update: When new features are added or architecture changes*