"""
Market calendar utilities for NYSE trading schedule.
Provides functions to check market status, holidays, and trading hours.
"""
from datetime import datetime, date, timedelta
from typing import Optional
import pytz
import pandas_market_calendars as mcal

# Initialize NYSE calendar once
_nyse_calendar = mcal.get_calendar('NYSE')
_eastern_tz = pytz.timezone('US/Eastern')


def is_market_open(check_date: Optional[date] = None) -> bool:
    """
    Check if the NYSE is open on a given date.
    
    Args:
        check_date: Date to check. If None, uses today.
        
    Returns:
        True if market is open, False if closed (holiday/weekend)
    """
    if check_date is None:
        check_date = datetime.now(_eastern_tz).date()
    
    try:
        # Get NYSE schedule for the given date
        schedule = _nyse_calendar.schedule(start_date=check_date, end_date=check_date)
        
        # If schedule is empty, market is closed
        is_open = len(schedule) > 0
        
        if not is_open:
            print(f"[{check_date}] NYSE is closed (holiday or weekend)")
        
        return is_open
        
    except Exception as e:
        print(f"Error checking market calendar: {e}")
        # Default to allowing trading if calendar check fails
        return True


def is_market_open_now() -> bool:
    """
    Check if the NYSE is currently open (both date and time).
    
    Returns:
        True if market is open right now, False otherwise
    """
    now = datetime.now(_eastern_tz)
    current_date = now.date()
    current_time = now.time()
    
    # Check if market is open today
    if not is_market_open(current_date):
        return False
    
    # Market hours: 9:30 AM - 4:00 PM ET
    market_open_time = datetime.strptime("09:30", "%H:%M").time()
    market_close_time = datetime.strptime("16:00", "%H:%M").time()
    
    return market_open_time <= current_time <= market_close_time


def get_next_trading_day(from_date: Optional[date] = None) -> date:
    """
    Get the next trading day after the given date.
    
    Args:
        from_date: Starting date. If None, uses today.
        
    Returns:
        Next valid trading day
    """
    if from_date is None:
        from_date = datetime.now(_eastern_tz).date()
    
    # Get schedule for next 10 days to find next trading day
    end_date = from_date + timedelta(days=10)
    schedule = _nyse_calendar.schedule(start_date=from_date, end_date=end_date)
    
    if len(schedule) > 0:
        return schedule.index[0].date()
    
    return from_date


def get_market_hours(check_date: Optional[date] = None) -> Optional[dict]:
    """
    Get market open and close times for a given date.
    
    Args:
        check_date: Date to check. If None, uses today.
        
    Returns:
        Dictionary with 'open' and 'close' times, or None if market closed
    """
    if check_date is None:
        check_date = datetime.now(_eastern_tz).date()
    
    schedule = _nyse_calendar.schedule(start_date=check_date, end_date=check_date)
    
    if len(schedule) == 0:
        return None
    
    row = schedule.iloc[0]
    return {
        "open": row['market_open'].to_pydatetime(),
        "close": row['market_close'].to_pydatetime(),
        "is_early_close": row['market_close'].hour < 16  # Normal close is 4 PM
    }


# For backwards compatibility
def is_market_open_today() -> bool:
    """Legacy function name - check if market is open today."""
    return is_market_open()
