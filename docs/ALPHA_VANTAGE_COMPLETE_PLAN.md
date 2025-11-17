# Alpha Vantage Complete Data Extraction Plan

## Overview

This document outlines a comprehensive plan to extract **ALL** data types available from Alpha Vantage API using the MCP server tools, not just fundamental data.

**Last Updated:** November 16, 2025

---

## Available Alpha Vantage MCP Tools

### 1. Core Stock Time Series (5 tools)
- `mcp_alphavantage_TIME_SERIES_INTRADAY` - Intraday OHLCV (1min, 5min, 15min, 30min, 60min)
- `mcp_alphavantage_TIME_SERIES_DAILY` - Daily OHLCV (20+ years)
- `mcp_alphavantage_TIME_SERIES_DAILY_ADJUSTED` - Daily with adjusted close + dividends/splits
- `mcp_alphavantage_TIME_SERIES_WEEKLY` - Weekly OHLCV (20+ years)
- `mcp_alphavantage_TIME_SERIES_WEEKLY_ADJUSTED` - Weekly with adjusted close
- `mcp_alphavantage_TIME_SERIES_MONTHLY` - Monthly OHLCV (20+ years)
- `mcp_alphavantage_TIME_SERIES_MONTHLY_ADJUSTED` - Monthly with adjusted close

### 2. Technical Indicators (40+ tools)
**Overlap Studies:**
- `mcp_alphavantage_SMA`, `mcp_alphavantage_EMA`, `mcp_alphavantage_WMA`, `mcp_alphavantage_DEMA`, `mcp_alphavantage_TEMA`, `mcp_alphavantage_TRIMA`
- `mcp_alphavantage_KAMA`, `mcp_alphavantage_MAMA`
- `mcp_alphavantage_VWAP`
- `mcp_alphavantage_T3`
- `mcp_alphavantage_BBANDS` (Bollinger Bands)
- `mcp_alphavantage_SAR` (Parabolic SAR)

**Momentum Indicators:**
- `mcp_alphavantage_MACD`, `mcp_alphavantage_MACDEXT`
- `mcp_alphavantage_STOCH`, `mcp_alphavantage_STOCHF`, `mcp_alphavantage_STOCHRSI`
- `mcp_alphavantage_RSI`
- `mcp_alphavantage_WILLR` (Williams %R)
- `mcp_alphavantage_ADX`, `mcp_alphavantage_ADXR`
- `mcp_alphavantage_APO`, `mcp_alphavantage_PPO`
- `mcp_alphavantage_MOM`, `mcp_alphavantage_BOP`
- `mcp_alphavantage_CCI` (Commodity Channel Index)
- `mcp_alphavantage_CMO` (Chande Momentum Oscillator)
- `mcp_alphavantage_ROC`, `mcp_alphavantage_ROCR`
- `mcp_alphavantage_AROON`, `mcp_alphavantage_AROONOSC`
- `mcp_alphavantage_MFI` (Money Flow Index)
- `mcp_alphavantage_TRIX`
- `mcp_alphavantage_ULTOSC` (Ultimate Oscillator)
- `mcp_alphavantage_DX`
- `mcp_alphavantage_MINUS_DI`, `mcp_alphavantage_PLUS_DI`, `mcp_alphavantage_MINUS_DM`, `mcp_alphavantage_PLUS_DM`

**Volume Indicators:**
- `mcp_alphavantage_AD` (Accumulation/Distribution)
- `mcp_alphavantage_ADOSC` (Chaikin A/D Oscillator)
- `mcp_alphavantage_OBV` (On Balance Volume)

**Volatility Indicators:**
- `mcp_alphavantage_ATR`, `mcp_alphavantage_NATR`
- `mcp_alphavantage_TRANGE`

**Price Transform:**
- `mcp_alphavantage_MIDPOINT`, `mcp_alphavantage_MIDPRICE`
- `mcp_alphavantage_AVGPRICE`

**Cycle Indicators (Hilbert Transform):**
- `mcp_alphavantage_HT_DCPERIOD`, `mcp_alphavantage_HT_DCPHASE`
- `mcp_alphavantage_HT_PHASOR`
- `mcp_alphavantage_HT_SINE`
- `mcp_alphavantage_HT_TRENDLINE`, `mcp_alphavantage_HT_TRENDMODE`

### 3. Fundamental Data (11 tools)
- **Company Overview**: Available via MCP (need to check exact function name)
- **Financial Statements**: Income Statement, Balance Sheet, Cash Flow
- **Corporate Actions**: Dividends (`mcp_alphavantage_SPLITS`), Splits
- **Shares Outstanding**: Quarterly shares data
- **Earnings**: Historical + Estimates
- **ETF Profile**: Holdings and metrics
- **Listing Status**: Active/delisted tracking

### 4. Forex & Cryptocurrencies (8 tools)
**Forex:**
- `mcp_alphavantage_FX_INTRADAY` - Intraday forex rates
- `mcp_alphavantage_FX_DAILY` - Daily forex rates
- `mcp_alphavantage_FX_WEEKLY` - Weekly forex rates
- `mcp_alphavantage_FX_MONTHLY` - Monthly forex rates
- `mcp_alphavantage_CURRENCY_EXCHANGE_RATE` - Real-time exchange rate

**Cryptocurrencies:**
- `mcp_alphavantage_CRYPTO_INTRADAY` - Intraday crypto prices
- `mcp_alphavantage_DIGITAL_CURRENCY_DAILY` - Daily crypto prices
- `mcp_alphavantage_DIGITAL_CURRENCY_WEEKLY` - Weekly crypto prices
- `mcp_alphavantage_DIGITAL_CURRENCY_MONTHLY` - Monthly crypto prices

### 5. Commodities (11 tools)
- `mcp_alphavantage_WTI` - WTI Crude Oil
- `mcp_alphavantage_BRENT` - Brent Crude Oil
- `mcp_alphavantage_NATURAL_GAS` - Natural Gas
- `mcp_alphavantage_COPPER` - Copper
- `mcp_alphavantage_ALUMINUM` - Aluminum
- `mcp_alphavantage_WHEAT` - Wheat
- `mcp_alphavantage_CORN` - Corn
- `mcp_alphavantage_COTTON` - Cotton
- `mcp_alphavantage_SUGAR` - Sugar
- `mcp_alphavantage_COFFEE` - Coffee
- `mcp_alphavantage_ALL_COMMODITIES` - All commodity price indices

### 6. Economic Indicators (6 tools)
- `mcp_alphavantage_REAL_GDP` - Real GDP
- `mcp_alphavantage_REAL_GDP_PER_CAPITA` - GDP per capita
- `mcp_alphavantage_TREASURY_YIELD` - Treasury yields
- `mcp_alphavantage_FEDERAL_FUNDS_RATE` - Federal funds rate
- `mcp_alphavantage_CPI` - Consumer Price Index (inflation)
- `mcp_alphavantage_INFLATION` - Inflation rate
- `mcp_alphavantage_RETAIL_SALES` - Retail sales
- `mcp_alphavantage_DURABLES` - Durable goods orders
- `mcp_alphavantage_UNEMPLOYMENT` - Unemployment rate
- `mcp_alphavantage_NONFARM_PAYROLL` - Non-farm payroll

### 7. Market Data & Search (4 tools)
- `mcp_alphavantage_SYMBOL_SEARCH` - Search for symbols
- `mcp_alphavantage_MARKET_STATUS` - Global market status
- `mcp_alphavantage_GLOBAL_QUOTE` - Latest price quote
- `mcp_alphavantage_TOP_GAINERS_LOSERS` - Top gainers/losers/most active
- `mcp_alphavantage_REALTIME_BULK_QUOTES` - Bulk quote retrieval
- `mcp_alphavantage_REALTIME_OPTIONS` - Options chain data

### 8. News & Sentiment (1 tool)
- `mcp_alphavantage_NEWS_SENTIMENT` - Live and historical news with sentiment

### 9. Advanced Analytics (2 tools)
- `mcp_alphavantage_ANALYTICS_FIXED_WINDOW` - Advanced metrics over fixed window
- `mcp_alphavantage_ANALYTICS_SLIDING_WINDOW` - Advanced metrics over sliding window

### 10. Utility Tools (2 tools)
- `mcp_alphavantage_FETCH` - Generic API call for any function
- `mcp_alphavantage_SEARCH` - Natural language search for Alpha Vantage data
- `mcp_alphavantage_PING` - Health check

---

## Complete Data Extraction Strategy

### Phase 1: Core Stock Data (Week 1-2)

#### 1.1 Historical Price Data
**Models:**
```python
class StockPriceHistory(Document):
    """Historical OHLCV data at various intervals."""
    ticker: str
    interval: str  # "daily", "weekly", "monthly", "1min", "5min", etc.
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    adjusted_close: Optional[float]
    volume: int
    dividend_amount: Optional[float]
    split_coefficient: Optional[float]
    
    class Settings:
        name = "stock_price_history"
        indexes = [
            IndexModel([("ticker", 1), ("interval", 1), ("timestamp", -1)]),
        ]
```

**Service Methods:**
```python
class AlphaVantageService:
    async def get_intraday_data(self, ticker: str, interval: str = "5min", 
                                outputsize: str = "compact") -> Optional[Dict]:
        """Fetch intraday OHLCV using mcp_alphavantage_TIME_SERIES_INTRADAY."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_TIME_SERIES_INTRADAY(
            symbol=ticker,
            interval=interval,
            outputsize=outputsize,
            entitlement="delayed"
        )
    
    async def get_daily_adjusted(self, ticker: str, outputsize: str = "full") -> Optional[Dict]:
        """Fetch daily adjusted prices with dividends/splits."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_TIME_SERIES_DAILY_ADJUSTED(
            symbol=ticker,
            outputsize=outputsize,
            entitlement="delayed"
        )
    
    async def get_weekly_adjusted(self, ticker: str) -> Optional[Dict]:
        """Fetch weekly adjusted prices."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_TIME_SERIES_WEEKLY_ADJUSTED(
            symbol=ticker,
            entitlement="delayed"
        )
    
    async def get_monthly_adjusted(self, ticker: str) -> Optional[Dict]:
        """Fetch monthly adjusted prices."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_TIME_SERIES_MONTHLY_ADJUSTED(
            symbol=ticker,
            entitlement="delayed"
        )
```

**Endpoints:**
- `GET /stocks/{ticker}/history/intraday` - Intraday prices with interval parameter
- `GET /stocks/{ticker}/history/daily` - Daily prices with date range
- `GET /stocks/{ticker}/history/weekly` - Weekly prices
- `GET /stocks/{ticker}/history/monthly` - Monthly prices

**Background Job:**
```python
class HistoricalDataCollectorJob:
    """Collect historical price data for all active tickers."""
    
    async def run(self):
        """
        Daily collection: Get yesterday's daily price for all tickers.
        Weekly collection (Sundays): Get weekly data.
        Monthly collection (1st of month): Get monthly data.
        """
        tickers = await get_active_tickers()
        
        # Daily: 1 call per ticker
        for ticker in tickers[:25]:  # Respect 25/day limit
            await self.collect_daily_price(ticker)
            await asyncio.sleep(15)  # Rate limiting
```

#### 1.2 Technical Indicators
**Models:**
```python
class TechnicalIndicator(Document):
    """Store calculated technical indicators."""
    ticker: str
    indicator_type: str  # "SMA", "EMA", "RSI", "MACD", etc.
    interval: str  # "daily", "weekly", "60min", etc.
    timestamp: datetime
    value: Dict  # Flexible field for indicator-specific values
    parameters: Dict  # Indicator parameters (e.g., {"time_period": 20})
    
    class Settings:
        name = "technical_indicators"
        indexes = [
            IndexModel([("ticker", 1), ("indicator_type", 1), ("timestamp", -1)]),
        ]
```

**Service Methods (40+ indicators):**
```python
class AlphaVantageService:
    # Moving Averages
    async def get_sma(self, ticker: str, interval: str, time_period: int, 
                     series_type: str = "close") -> Optional[Dict]:
        """Simple Moving Average."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_SMA(
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            series_type=series_type
        )
    
    async def get_ema(self, ticker: str, interval: str, time_period: int, 
                     series_type: str = "close") -> Optional[Dict]:
        """Exponential Moving Average."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_EMA(
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            series_type=series_type
        )
    
    # Momentum Indicators
    async def get_rsi(self, ticker: str, interval: str, time_period: int = 14, 
                     series_type: str = "close") -> Optional[Dict]:
        """Relative Strength Index."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_RSI(
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            series_type=series_type
        )
    
    async def get_macd(self, ticker: str, interval: str, series_type: str = "close",
                      fastperiod: int = 12, slowperiod: int = 26, 
                      signalperiod: int = 9) -> Optional[Dict]:
        """MACD (Moving Average Convergence Divergence)."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_MACD(
            symbol=ticker,
            interval=interval,
            series_type=series_type,
            fastperiod=fastperiod,
            slowperiod=slowperiod,
            signalperiod=signalperiod
        )
    
    async def get_stoch(self, ticker: str, interval: str, 
                       fastkperiod: int = 5, slowkperiod: int = 3, 
                       slowdperiod: int = 3) -> Optional[Dict]:
        """Stochastic Oscillator."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_STOCH(
            symbol=ticker,
            interval=interval,
            fastkperiod=fastkperiod,
            slowkperiod=slowkperiod,
            slowdperiod=slowdperiod
        )
    
    # Volatility Indicators
    async def get_bbands(self, ticker: str, interval: str, time_period: int = 20,
                        series_type: str = "close", nbdevup: int = 2, 
                        nbdevdn: int = 2) -> Optional[Dict]:
        """Bollinger Bands."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_BBANDS(
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
            nbdevup=nbdevup,
            nbdevdn=nbdevdn
        )
    
    async def get_atr(self, ticker: str, interval: str, 
                     time_period: int = 14) -> Optional[Dict]:
        """Average True Range."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_ATR(
            symbol=ticker,
            interval=interval,
            time_period=time_period
        )
    
    # Volume Indicators
    async def get_obv(self, ticker: str, interval: str) -> Optional[Dict]:
        """On Balance Volume."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_OBV(
            symbol=ticker,
            interval=interval
        )
    
    async def get_ad(self, ticker: str, interval: str) -> Optional[Dict]:
        """Accumulation/Distribution Line."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_AD(
            symbol=ticker,
            interval=interval
        )
    
    # ... (30+ more indicator methods)
```

**Endpoints:**
```python
# Grouped by category for better API organization
@router.get("/stocks/{ticker}/indicators/moving-averages")
async def get_moving_averages(ticker: str, interval: str = "daily"):
    """Get all moving averages (SMA, EMA, WMA, DEMA, etc.)."""
    pass

@router.get("/stocks/{ticker}/indicators/momentum")
async def get_momentum_indicators(ticker: str, interval: str = "daily"):
    """Get momentum indicators (RSI, MACD, Stochastic, etc.)."""
    pass

@router.get("/stocks/{ticker}/indicators/volatility")
async def get_volatility_indicators(ticker: str, interval: str = "daily"):
    """Get volatility indicators (Bollinger Bands, ATR, etc.)."""
    pass

@router.get("/stocks/{ticker}/indicators/volume")
async def get_volume_indicators(ticker: str, interval: str = "daily"):
    """Get volume indicators (OBV, AD, MFI, etc.)."""
    pass

@router.get("/stocks/{ticker}/indicators/{indicator_name}")
async def get_specific_indicator(ticker: str, indicator_name: str, 
                                interval: str = "daily"):
    """Get specific indicator with custom parameters."""
    pass
```

**Background Job:**
```python
class TechnicalIndicatorsJob:
    """Calculate and store key technical indicators daily."""
    
    CORE_INDICATORS = [
        ("SMA", {"time_period": 20}),
        ("SMA", {"time_period": 50}),
        ("SMA", {"time_period": 200}),
        ("EMA", {"time_period": 12}),
        ("EMA", {"time_period": 26}),
        ("RSI", {"time_period": 14}),
        ("MACD", {"fastperiod": 12, "slowperiod": 26}),
        ("BBANDS", {"time_period": 20}),
        ("ATR", {"time_period": 14}),
        ("OBV", {}),
    ]
    
    async def run(self):
        """
        Calculate core indicators for all active tickers.
        10 indicators × 25 tickers = 250 calls (needs 10 days with 25/day limit).
        Alternative: Calculate 2-3 tickers fully per day.
        """
        pass
```

### Phase 2: Fundamental Data (Week 3) - ALREADY PLANNED
See previous plan for comprehensive fundamental data extraction.

### Phase 3: Forex & Cryptocurrencies (Week 4)

#### 3.1 Forex Data
**Models:**
```python
class ForexRate(Document):
    """Foreign exchange rates."""
    from_currency: str  # "USD"
    to_currency: str    # "EUR"
    interval: str       # "intraday", "daily", "weekly", "monthly"
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    
    class Settings:
        name = "forex_rates"
        indexes = [
            IndexModel([("from_currency", 1), ("to_currency", 1), ("timestamp", -1)]),
        ]

class CurrencyExchangeRate(Document):
    """Real-time exchange rates."""
    from_currency: str
    to_currency: str
    exchange_rate: float
    bid_price: float
    ask_price: float
    timestamp: datetime
    
    class Settings:
        name = "currency_exchange_rates"
        indexes = [
            IndexModel([("from_currency", 1), ("to_currency", 1), ("timestamp", -1)]),
        ]
```

**Service Methods:**
```python
class AlphaVantageService:
    async def get_forex_intraday(self, from_currency: str, to_currency: str, 
                                interval: str = "5min") -> Optional[Dict]:
        """Intraday forex rates."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_FX_INTRADAY(
            from_symbol=from_currency,
            to_symbol=to_currency,
            interval=interval
        )
    
    async def get_forex_daily(self, from_currency: str, 
                             to_currency: str) -> Optional[Dict]:
        """Daily forex rates."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_FX_DAILY(
            from_symbol=from_currency,
            to_symbol=to_currency
        )
    
    async def get_exchange_rate(self, from_currency: str, 
                               to_currency: str) -> Optional[Dict]:
        """Real-time exchange rate."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_CURRENCY_EXCHANGE_RATE(
            from_currency=from_currency,
            to_currency=to_currency
        )
```

**Endpoints:**
- `GET /forex/{from_currency}/{to_currency}/intraday`
- `GET /forex/{from_currency}/{to_currency}/daily`
- `GET /forex/{from_currency}/{to_currency}/rate` - Real-time rate

#### 3.2 Cryptocurrency Data
**Models:**
```python
class CryptocurrencyPrice(Document):
    """Cryptocurrency prices."""
    symbol: str         # "BTC", "ETH"
    market: str         # "USD", "EUR"
    interval: str       # "intraday", "daily", "weekly", "monthly"
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    market_cap: Optional[float]
    
    class Settings:
        name = "cryptocurrency_prices"
        indexes = [
            IndexModel([("symbol", 1), ("market", 1), ("timestamp", -1)]),
        ]
```

**Service Methods:**
```python
class AlphaVantageService:
    async def get_crypto_intraday(self, symbol: str, market: str = "USD", 
                                  interval: str = "5min") -> Optional[Dict]:
        """Intraday crypto prices."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_CRYPTO_INTRADAY(
            symbol=symbol,
            market=market,
            interval=interval
        )
    
    async def get_crypto_daily(self, symbol: str, 
                              market: str = "USD") -> Optional[Dict]:
        """Daily crypto prices."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_DIGITAL_CURRENCY_DAILY(
            symbol=symbol,
            market=market
        )
```

**Endpoints:**
- `GET /crypto/{symbol}/intraday`
- `GET /crypto/{symbol}/daily`
- `GET /crypto/{symbol}/weekly`
- `GET /crypto/{symbol}/monthly`

### Phase 4: Commodities & Economic Indicators (Week 5)

#### 4.1 Commodities
**Models:**
```python
class CommodityPrice(Document):
    """Commodity price indices."""
    commodity: str      # "WTI", "BRENT", "GOLD", "SILVER", etc.
    interval: str       # "monthly", "quarterly", "annual"
    date: str           # "2025-11" or "2025-Q4"
    value: float
    unit: str           # "USD/barrel", "USD/ounce"
    
    class Settings:
        name = "commodity_prices"
        indexes = [
            IndexModel([("commodity", 1), ("date", -1)]),
        ]
```

**Service Methods:**
```python
class AlphaVantageService:
    async def get_wti_crude(self, interval: str = "monthly") -> Optional[Dict]:
        """WTI crude oil prices."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_WTI(interval=interval)
    
    async def get_brent_crude(self, interval: str = "monthly") -> Optional[Dict]:
        """Brent crude oil prices."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_BRENT(interval=interval)
    
    async def get_natural_gas(self, interval: str = "monthly") -> Optional[Dict]:
        """Natural gas prices."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_NATURAL_GAS(interval=interval)
    
    async def get_all_commodities(self) -> Optional[Dict]:
        """All commodity price indices."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_ALL_COMMODITIES()
    
    # ... (8 more commodity methods)
```

**Endpoints:**
- `GET /commodities/oil/wti`
- `GET /commodities/oil/brent`
- `GET /commodities/metals/copper`
- `GET /commodities/metals/aluminum`
- `GET /commodities/agriculture/wheat`
- `GET /commodities/agriculture/corn`
- `GET /commodities/all` - All indices

#### 4.2 Economic Indicators
**Models:**
```python
class EconomicIndicator(Document):
    """Economic indicators (GDP, CPI, unemployment, etc.)."""
    indicator_type: str  # "REAL_GDP", "CPI", "UNEMPLOYMENT", etc.
    country: str         # "US", default
    date: str            # "2025-Q3" or "2025-11"
    value: float
    unit: Optional[str]  # "billions of dollars", "percent", etc.
    
    class Settings:
        name = "economic_indicators"
        indexes = [
            IndexModel([("indicator_type", 1), ("date", -1)]),
        ]
```

**Service Methods:**
```python
class AlphaVantageService:
    async def get_real_gdp(self, interval: str = "quarterly") -> Optional[Dict]:
        """Real GDP."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_REAL_GDP(interval=interval)
    
    async def get_cpi(self, interval: str = "monthly") -> Optional[Dict]:
        """Consumer Price Index."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_CPI(interval=interval)
    
    async def get_unemployment(self) -> Optional[Dict]:
        """Unemployment rate."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_UNEMPLOYMENT()
    
    async def get_federal_funds_rate(self, interval: str = "monthly") -> Optional[Dict]:
        """Federal funds rate."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_FEDERAL_FUNDS_RATE(interval=interval)
    
    # ... (6 more economic indicator methods)
```

**Endpoints:**
- `GET /economy/gdp`
- `GET /economy/inflation/cpi`
- `GET /economy/unemployment`
- `GET /economy/interest-rates/federal-funds`
- `GET /economy/retail-sales`

### Phase 5: Market Data & News (Week 6)

#### 5.1 Market Data
**Models:**
```python
class GlobalQuote(Document):
    """Latest price quote."""
    ticker: str
    price: float
    change: float
    change_percent: float
    volume: int
    latest_trading_day: str
    previous_close: float
    open: float
    high: float
    low: float
    timestamp: datetime
    
    class Settings:
        name = "global_quotes"
        indexes = [
            IndexModel([("ticker", 1), ("timestamp", -1)]),
        ]

class MarketMovers(Document):
    """Top gainers, losers, most active."""
    category: str  # "gainers", "losers", "most_active"
    ticker: str
    price: float
    change_amount: float
    change_percentage: float
    volume: int
    timestamp: datetime
    
    class Settings:
        name = "market_movers"
        indexes = [
            IndexModel([("category", 1), ("timestamp", -1)]),
        ]

class OptionsChain(Document):
    """Options data."""
    underlying_ticker: str
    option_type: str    # "call", "put"
    strike: float
    expiry_date: str
    bid: float
    ask: float
    volume: int
    open_interest: int
    implied_volatility: Optional[float]
    timestamp: datetime
    
    class Settings:
        name = "options_chains"
        indexes = [
            IndexModel([("underlying_ticker", 1), ("expiry_date", 1)]),
        ]
```

**Service Methods:**
```python
class AlphaVantageService:
    async def get_global_quote(self, ticker: str) -> Optional[Dict]:
        """Latest price quote."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_GLOBAL_QUOTE(symbol=ticker)
    
    async def get_top_gainers_losers(self) -> Optional[Dict]:
        """Top gainers, losers, most active."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_TOP_GAINERS_LOSERS()
    
    async def get_market_status(self) -> Optional[Dict]:
        """Global market status."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_MARKET_STATUS()
    
    async def get_bulk_quotes(self, symbols: List[str]) -> Optional[Dict]:
        """Bulk quote retrieval."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_REALTIME_BULK_QUOTES(symbols=",".join(symbols))
    
    async def get_options_chain(self, ticker: str) -> Optional[Dict]:
        """Options chain data."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_REALTIME_OPTIONS(symbol=ticker)
    
    async def search_symbol(self, keywords: str) -> Optional[Dict]:
        """Search for symbols."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_SYMBOL_SEARCH(keywords=keywords)
```

**Endpoints:**
- `GET /market/quote/{ticker}` - Latest quote
- `GET /market/movers` - Top gainers/losers/active
- `GET /market/status` - Market hours status
- `POST /market/quotes/bulk` - Bulk quotes
- `GET /market/options/{ticker}` - Options chain
- `GET /market/search` - Symbol search

#### 5.2 News & Sentiment
**Models:**
```python
class NewsArticle(Document):
    """News articles with sentiment."""
    title: str
    url: str
    time_published: datetime
    authors: List[str]
    summary: str
    source: str
    category_within_source: Optional[str]
    source_domain: str
    topics: List[Dict]  # [{"topic": "Technology", "relevance_score": "0.9"}]
    overall_sentiment_score: float
    overall_sentiment_label: str
    ticker_sentiment: List[Dict]  # [{"ticker": "AAPL", "relevance_score": "0.8", "sentiment_score": 0.5}]
    
    class Settings:
        name = "news_articles"
        indexes = [
            IndexModel([("time_published", -1)]),
            IndexModel([("ticker_sentiment.ticker", 1), ("time_published", -1)]),
        ]
```

**Service Methods:**
```python
class AlphaVantageService:
    async def get_news_sentiment(self, tickers: Optional[List[str]] = None, 
                                 topics: Optional[List[str]] = None,
                                 time_from: Optional[str] = None,
                                 time_to: Optional[str] = None,
                                 limit: int = 50) -> Optional[Dict]:
        """News and sentiment data."""
        await self.rate_limiter.acquire()
        
        params = {"limit": limit}
        if tickers:
            params["tickers"] = ",".join(tickers)
        if topics:
            params["topics"] = ",".join(topics)
        if time_from:
            params["time_from"] = time_from
        if time_to:
            params["time_to"] = time_to
        
        return await mcp_alphavantage_NEWS_SENTIMENT(**params)
```

**Endpoints:**
- `GET /news` - Latest news across all stocks
- `GET /news/ticker/{ticker}` - News for specific ticker
- `GET /news/sentiment` - News with sentiment analysis

### Phase 6: Advanced Analytics (Week 7)

#### 6.1 Advanced Analytics
**Models:**
```python
class AdvancedMetrics(Document):
    """Advanced analytics metrics."""
    ticker: str
    calculation_type: str  # "fixed_window", "sliding_window"
    window_size: int       # Days or periods
    metric_type: str       # "volatility", "returns", "correlation", etc.
    timestamp: datetime
    metrics: Dict          # Flexible field for various metric types
    
    class Settings:
        name = "advanced_metrics"
        indexes = [
            IndexModel([("ticker", 1), ("metric_type", 1), ("timestamp", -1)]),
        ]
```

**Service Methods:**
```python
class AlphaVantageService:
    async def get_fixed_window_analytics(self, ticker: str, range: str, 
                                        interval: str, ohlc: str,
                                        window_size: int, 
                                        calculations: str) -> Optional[Dict]:
        """Advanced metrics over fixed window."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_ANALYTICS_FIXED_WINDOW(
            SYMBOLS=ticker,
            RANGE=range,
            INTERVAL=interval,
            OHLC=ohlc,
            WINDOW_SIZE=window_size,
            CALCULATIONS=calculations
        )
    
    async def get_sliding_window_analytics(self, ticker: str, range: str,
                                          interval: str, ohlc: str,
                                          window_size: int,
                                          calculations: str) -> Optional[Dict]:
        """Advanced metrics over sliding window."""
        await self.rate_limiter.acquire()
        return await mcp_alphavantage_ANALYTICS_SLIDING_WINDOW(
            SYMBOLS=ticker,
            RANGE=range,
            INTERVAL=interval,
            OHLC=ohlc,
            WINDOW_SIZE=window_size,
            CALCULATIONS=calculations
        )
```

**Endpoints:**
- `GET /analytics/{ticker}/fixed-window`
- `GET /analytics/{ticker}/sliding-window`

---

## Implementation Summary

### Total API Coverage

| Category | MCP Tools Available | Models Needed | Service Methods | Endpoints |
|----------|-------------------|---------------|-----------------|-----------|
| **Time Series** | 7 | 1 | 7 | 4 |
| **Technical Indicators** | 40+ | 1 | 40+ | 5 |
| **Fundamental Data** | 11 | 4 | 7 | 7 |
| **Forex** | 5 | 2 | 5 | 3 |
| **Cryptocurrency** | 4 | 1 | 4 | 4 |
| **Commodities** | 11 | 1 | 11 | 7 |
| **Economic Indicators** | 10 | 1 | 10 | 5 |
| **Market Data** | 6 | 3 | 6 | 6 |
| **News & Sentiment** | 1 | 1 | 1 | 3 |
| **Advanced Analytics** | 2 | 1 | 2 | 2 |
| **TOTAL** | **98+** | **17** | **93+** | **46+** |

### Rate Limiting Strategy

**Critical Constraints:**
- 5 calls per minute
- 25 calls per day
- Must support 90+ API functions

**Solution: Multi-Tier Collection Strategy**

#### Tier 1: Real-Time (Every Minute)
- `GLOBAL_QUOTE` for active tickers during market hours
- **Budget**: 5 tickers/minute max = 300 tickers/hour during trading

#### Tier 2: Frequent (Hourly)
- Market movers (gainers/losers)
- News sentiment
- **Budget**: 1-2 calls/hour = 24-48 calls/day (use non-trading hours)

#### Tier 3: Daily (Once per day)
- Daily adjusted prices
- Core technical indicators (SMA, EMA, RSI, MACD)
- **Budget**: 10-15 calls/day during off-market hours

#### Tier 4: Weekly (Once per week)
- Weekly adjusted prices
- Full technical indicator suite
- Forex rates
- Cryptocurrency prices
- **Budget**: 25 calls on Sunday (full daily allowance)

#### Tier 5: Monthly (Once per month)
- Monthly adjusted prices
- Commodities
- Economic indicators
- **Budget**: 25 calls on 1st of month

#### Tier 6: Quarterly (Once per quarter)
- Fundamental data (income statement, balance sheet, cash flow)
- Dividends, splits, shares outstanding
- **Budget**: 25 calls spread over multiple days per ticker

### Background Job Architecture

```python
# backend/app/services/scheduler/registry.py

def register_all_jobs():
    # Tier 1: Real-time (market hours only)
    job_scheduler.add_job(
        func=realtime_quote_job.run,
        trigger=CronTrigger(minute='*/1', day_of_week='mon-fri', hour='9-16'),
        job_id='realtime_quotes',
        name='Real-time Quote Collection'
    )
    
    # Tier 2: Hourly
    job_scheduler.add_job(
        func=market_movers_job.run,
        trigger=CronTrigger(minute=5),  # Every hour at :05
        job_id='market_movers',
        name='Market Movers Collection'
    )
    
    job_scheduler.add_job(
        func=news_sentiment_job.run,
        trigger=CronTrigger(minute=35),  # Every hour at :35
        job_id='news_sentiment',
        name='News Sentiment Collection'
    )
    
    # Tier 3: Daily (off-market hours)
    job_scheduler.add_job(
        func=daily_prices_job.run,
        trigger=CronTrigger(hour=18, minute=0),  # 6 PM EST
        job_id='daily_prices',
        name='Daily Price Collection'
    )
    
    job_scheduler.add_job(
        func=core_indicators_job.run,
        trigger=CronTrigger(hour=19, minute=0),  # 7 PM EST
        job_id='core_indicators',
        name='Core Technical Indicators'
    )
    
    # Tier 4: Weekly (Sundays)
    job_scheduler.add_job(
        func=weekly_data_job.run,
        trigger=CronTrigger(day_of_week='sun', hour=2, minute=0),
        job_id='weekly_data',
        name='Weekly Data Collection'
    )
    
    # Tier 5: Monthly (1st of month)
    job_scheduler.add_job(
        func=monthly_data_job.run,
        trigger=CronTrigger(day=1, hour=3, minute=0),
        job_id='monthly_data',
        name='Monthly Data Collection'
    )
    
    # Tier 6: Quarterly (every 3 months)
    job_scheduler.add_job(
        func=fundamentals_collector_job.run,
        trigger=CronTrigger(month='*/3', day=1, hour=4, minute=0),
        job_id='fundamentals_collection',
        name='Quarterly Fundamentals Collection'
    )
```

### Cache Strategy

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Real-time quotes | 1 minute | High frequency updates |
| Intraday prices | 1 hour | Minute-level data |
| Daily prices | 24 hours | Daily updates |
| Weekly/Monthly prices | 7 days | Less frequent updates |
| Technical indicators | 24 hours | Recalculate daily |
| Fundamental data | 90 days | Quarterly reporting |
| Dividends | 30 days | Monthly check |
| Splits | 365 days | Rare events |
| Forex rates | 1 hour | Frequent changes |
| Crypto prices | 5 minutes | High volatility |
| Commodities | 30 days | Monthly updates |
| Economic indicators | 30 days | Monthly/quarterly releases |
| News | No cache | Real-time priority |
| Market movers | 1 hour | Hourly updates |
| Options | 15 minutes | Intraday volatility |

### Priority Implementation Order

**Phase 1 (Week 1-2): Core Stock Data** ✅ CRITICAL
- Historical prices (daily, weekly, monthly)
- Core technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
- Real-time quotes

**Phase 2 (Week 3): Fundamental Data** ✅ HIGH PRIORITY
- Already planned - see previous documentation

**Phase 3 (Week 4): Extended Technical Indicators** ⭐ HIGH VALUE
- Momentum indicators (Stochastic, Williams %R, ROC)
- Volume indicators (OBV, AD, MFI)
- Volatility indicators (ATR, NATR)
- Cycle indicators (Hilbert Transform suite)

**Phase 4 (Week 5): Market Data & Search** ⭐ HIGH VALUE
- Market movers (gainers/losers)
- Symbol search
- Options chain
- Bulk quotes

**Phase 5 (Week 6): News & Sentiment** ⭐ USER FACING
- News articles with sentiment
- Ticker-specific news
- Topic-based news

**Phase 6 (Week 7): Forex & Crypto** ⚠️ OPTIONAL
- Forex rates (if expanding beyond US stocks)
- Cryptocurrency prices (if adding crypto tracking)

**Phase 7 (Week 8): Commodities & Economics** ⚠️ OPTIONAL
- Commodity prices
- Economic indicators (for macro analysis)

**Phase 8 (Week 9): Advanced Analytics** 🔬 ADVANCED
- Fixed window analytics
- Sliding window analytics
- Custom metric calculations

---

## API Call Budget Planning

### Example: Full Implementation for 50 Tickers

#### Daily Budget (25 calls/day):
- **Real-time quotes**: 5 tickers × 60 mins × 8 hours = 2400 quotes/day (via 1/min job)
  - Uses 0 daily calls (collected via minute-based jobs)
- **Daily prices**: 20 tickers × 1 call = 20 calls
- **Core indicators**: 5 tickers × 1 indicator = 5 calls
- **TOTAL**: 25 calls/day ✅

#### Weekly Budget (25 calls on Sunday):
- **Weekly prices**: 50 tickers × 1 call = 50 calls
  - Split over 2 Sundays = 25 calls/Sunday ✅
- **Full indicator suite**: 10 tickers × 5 indicators = 50 calls
  - Rotate tickers weekly

#### Monthly Budget (25 calls on 1st):
- **Monthly prices**: 25 tickers
- **Commodities**: ALL_COMMODITIES (1 call) + specific commodities (10 calls)
- **Economic indicators**: 14 calls
- **TOTAL**: 25 calls ✅

#### Quarterly Budget (25 calls/day for 1 week):
- **Fundamental data**: 5 tickers × 7 calls = 35 calls
  - Spread over 2 days = 17-18 calls/day ✅
- Process 10-15 tickers per quarter

### Scalability:
- 50 active tickers supported with current limits
- Real-time tracking for top 5 tickers during market hours
- Full historical + technical for all 50 tickers
- Fundamental data for 10-15 tickers per quarter
- Can scale to 100 tickers by reducing indicator frequency or upgrading to premium tier

---

## Testing Strategy

### Unit Tests
```python
# Test each service method
async def test_get_sma():
    result = await alpha_vantage_service.get_sma("AAPL", "daily", 20, "close")
    assert result is not None
    assert "Technical Analysis: SMA" in result

# Test rate limiting
async def test_rate_limiter_respects_limits():
    rate_limiter = AlphaVantageRateLimiter()
    
    # Make 5 calls quickly (should work)
    for _ in range(5):
        await rate_limiter.acquire()
    
    # 6th call should wait
    start = time.time()
    await rate_limiter.acquire()
    duration = time.time() - start
    assert duration > 0  # Had to wait

# Test model validation
def test_technical_indicator_model():
    indicator = TechnicalIndicator(
        ticker="AAPL",
        indicator_type="SMA",
        interval="daily",
        timestamp=datetime.now(),
        value={"SMA": 150.0},
        parameters={"time_period": 20}
    )
    assert indicator.ticker == "AAPL"
```

### Integration Tests
```python
# Test full workflow
async def test_collect_and_store_sma():
    # Fetch from Alpha Vantage
    data = await alpha_vantage_service.get_sma("AAPL", "daily", 20, "close")
    
    # Parse and save
    parsed = parse_sma_response(data)
    await repository.save_technical_indicator(parsed)
    
    # Verify in database
    retrieved = await repository.get_technical_indicators(
        ticker="AAPL",
        indicator_type="SMA"
    )
    assert len(retrieved) > 0
```

### API Endpoint Tests
```python
# Test endpoints
async def test_get_indicators_endpoint():
    response = client.get("/stocks/AAPL/indicators/moving-averages")
    assert response.status_code == 200
    data = response.json()
    assert "SMA" in data
    assert "EMA" in data
```

---

## Documentation Requirements

### API Documentation (docs/API.md)
- Document all 46+ endpoints with examples
- Include request/response formats
- Document query parameters and filters
- Add caching behavior notes
- Rate limiting information

### Postman Collection
- Create comprehensive collection with all endpoints
- Group by category (Time Series, Indicators, Fundamental, etc.)
- Include example requests with parameters
- Add environment variables for API keys

### Architecture Documentation
- Update ARCHITECTURE.md with new services
- Document multi-tier collection strategy
- Explain rate limiting architecture
- Add data flow diagrams

---

## Monitoring & Alerting

### Metrics to Track
- API calls per minute/day/month
- Cache hit/miss rates
- Background job success/failure rates
- Data freshness (last update timestamp)
- Storage growth rate

### Alerts
- Daily API limit approaching 80% (20 calls)
- Rate limiter blocking requests frequently
- Background job failures
- Data staleness (no updates in 2+ days)
- Database storage exceeding thresholds

### Logging
```python
logger.info(
    "Alpha Vantage API call",
    extra={
        "function": "SMA",
        "ticker": "AAPL",
        "rate_limit_remaining_minute": 3,
        "rate_limit_remaining_daily": 18
    }
)
```

---

## Future Enhancements

### Premium Tier Considerations
- If upgrading to premium (120 calls/min, unlimited daily):
  - Increase real-time tracking to all tickers
  - Calculate all indicators daily
  - Enable user-triggered on-demand calculations
  - Add minute-level indicator calculations

### User Features
- Custom indicator configurations
- Saved indicator watchlists
- Alert triggers based on indicators (e.g., RSI > 70)
- Comparative analysis across tickers
- Custom technical analysis screeners

### Advanced Analytics
- Backtesting engine using historical data
- Custom indicator creation (combine existing indicators)
- Portfolio correlation analysis
- Sector/industry trend analysis using economic indicators
- Machine learning models using indicator data

---

## Risk Mitigation

### API Rate Limit Exhaustion
- **Risk**: Hitting 25/day limit too quickly
- **Mitigation**: 
  - Multi-tier job scheduling
  - Aggressive caching with appropriate TTLs
  - Priority queuing (critical data first)
  - Alert at 80% usage

### Data Staleness
- **Risk**: Data becoming outdated if collection fails
- **Mitigation**:
  - Monitor last update timestamps
  - Automatic retry with exponential backoff
  - Fallback to cached data with staleness warning
  - Alert on 2+ day staleness

### Storage Growth
- **Risk**: Historical data accumulating rapidly
- **Mitigation**:
  - Implement data retention policies (keep 2 years max)
  - Archive old data to cold storage
  - Compress historical indicator data
  - Monitor database size

### API Changes
- **Risk**: Alpha Vantage API structure changes
- **Mitigation**:
  - Version API response parsers
  - Comprehensive error handling
  - Fallback to raw data storage if parsing fails
  - Monitor API response structure changes

---

## Success Metrics

### Technical Metrics
- ✅ 98+ Alpha Vantage MCP tools integrated
- ✅ 17 new MongoDB models created
- ✅ 93+ service methods implemented
- ✅ 46+ API endpoints deployed
- ✅ <1 second response time for cached data
- ✅ 95%+ cache hit rate for historical data
- ✅ 99%+ background job success rate

### Business Metrics
- ✅ Support 50+ active tickers
- ✅ Real-time tracking during market hours
- ✅ Complete fundamental data for key holdings
- ✅ 40+ technical indicators calculated daily
- ✅ News sentiment analysis available
- ✅ Multi-asset class support (stocks, forex, crypto, commodities)

---

**Ready to proceed with Phase 1 implementation?**

This plan provides comprehensive coverage of ALL Alpha Vantage capabilities using MCP server tools. The multi-tier collection strategy ensures sustainable operation within the 25 calls/day limit while maximizing data coverage.
