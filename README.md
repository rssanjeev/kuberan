# Investment Projection Tool

A Python application for projecting investment growth with dividend reinvestment strategies.

## Architecture

The application has been refactored into an object-oriented design with the following structure:

### Models (`models/`)
- **`config.py`**: Configuration management using environment variables
- **`stock.py`**: Stock data model with financial information
- **`investment.py`**: Investment strategy model and portfolio projection logic

### Services (`services/`)
- **`data_scraper.py`**: Stock data scraping services (StockAnalysis, Yahoo Finance)
- **`report_service.py`**: CSV report generation service

### Application (`app.py`)
- **`InvestmentProjectionApp`**: Main application orchestrator

## Configuration

The application uses a `.env` file for configuration:

```env
# Investment Strategy Configuration
QUARTERS=12
TICKER=VXUS

# Strategy format: name:initial_amount:monthly_amount
STRATEGY_1=Safe:1000:100
STRATEGY_2=Moderate:2500:200
STRATEGY_3=Growth:3500:350
STRATEGY_4=Aggressive:5000:500
```

## Usage

```bash
# Run with default ticker from .env
python main.py

# Run with specific ticker
python main.py SCHD
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Features

- **Object-oriented design** with clear separation of concerns
- **Configurable strategies** via environment variables
- **Multiple data sources** with fallback scraping
- **Type hints** for better code documentation
- **Modular architecture** for easy testing and maintenance
- **CSV report generation** with detailed projections

## Output

The application generates a CSV file in the `Reports/Projections/` directory with quarterly projections showing:
- Strategy name and quarter
- Initial and quarterly investments
- Total shares accumulated
- Total investment amount
- Projected balance with dividend reinvestment

Output files are named: `Reports/Projections/{TICKER}_projection.csv`