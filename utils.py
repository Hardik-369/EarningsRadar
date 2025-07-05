import pandas as pd
from datetime import datetime, timedelta
import logging
import os
from io import StringIO
import csv

def setup_logging():
    """
    Setup logging configuration
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('earnings_radar.log'),
            logging.StreamHandler()
        ]
    )

def format_date(date_obj):
    """
    Format date object for display
    """
    if pd.isna(date_obj):
        return ""
    
    if isinstance(date_obj, str):
        return date_obj
    
    try:
        return date_obj.strftime('%Y-%m-%d')
    except:
        return str(date_obj)

def export_to_csv(df: pd.DataFrame) -> str:
    """
    Export DataFrame to CSV string
    """
    output = StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()

def create_ical_event(ticker: str, company: str, date: datetime, time: str) -> str:
    """
    Create iCalendar event for earnings call
    """
    event_start = date.strftime('%Y%m%dT090000Z')  # Default to 9 AM UTC
    event_end = date.strftime('%Y%m%dT100000Z')    # 1 hour duration
    
    # Adjust time if specified
    if 'pre' in time.lower():
        event_start = date.strftime('%Y%m%dT130000Z')  # 9 AM ET = 1 PM UTC
        event_end = date.strftime('%Y%m%dT140000Z')
    elif 'after' in time.lower():
        event_start = date.strftime('%Y%m%dT210000Z')  # 5 PM ET = 9 PM UTC
        event_end = date.strftime('%Y%m%dT220000Z')
    
    event = f"""BEGIN:VEVENT
DTSTART:{event_start}
DTEND:{event_end}
SUMMARY:{ticker} Earnings Call
DESCRIPTION:Earnings call for {company} ({ticker})
LOCATION:Conference Call
END:VEVENT
"""
    return event

def create_ical_calendar(earnings_df: pd.DataFrame) -> str:
    """
    Create full iCalendar file with all earnings events
    """
    calendar_header = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//EarningsRadar//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:Earnings Calendar
X-WR-TIMEZONE:America/New_York
"""
    
    calendar_footer = "END:VCALENDAR"
    
    events = []
    for _, row in earnings_df.iterrows():
        event = create_ical_event(
            row['ticker'], 
            row['company'], 
            row['date'], 
            row['time']
        )
        events.append(event)
    
    return calendar_header + "\n".join(events) + calendar_footer

def filter_recent_dates(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """
    Filter DataFrame to include only recent dates
    """
    if df.empty:
        return df
    
    cutoff_date = datetime.now() - timedelta(days=days)
    return df[df['date'] >= cutoff_date]

def get_market_hours(date_obj: datetime) -> dict:
    """
    Get market hours for a given date
    """
    # Simple market hours (Eastern Time)
    return {
        'pre_market_start': '04:00',
        'market_open': '09:30',
        'market_close': '16:00',
        'after_hours_end': '20:00'
    }

def clean_ticker(ticker: str) -> str:
    """
    Clean and standardize ticker symbol
    """
    if not ticker:
        return ""
    
    # Remove common suffixes and clean
    ticker = ticker.upper().strip()
    
    # Remove common exchange suffixes
    suffixes = ['-USD', '-US', '.US', '.TO', '.L']
    for suffix in suffixes:
        if ticker.endswith(suffix):
            ticker = ticker[:-len(suffix)]
    
    # Remove dots (but after suffix removal)
    ticker = ticker.replace('.', '')
    
    return ticker

def validate_ticker(ticker: str) -> bool:
    """
    Basic validation for ticker symbols
    """
    if not ticker:
        return False
    
    ticker = clean_ticker(ticker)
    
    # Basic checks
    if len(ticker) < 1 or len(ticker) > 5:
        return False
    
    if not ticker.isalpha():
        return False
    
    return True

def get_earnings_time_category(time_str: str) -> str:
    """
    Categorize earnings time into pre-market, market hours, or after-hours
    """
    if not time_str:
        return "Unknown"
    
    time_lower = time_str.lower()
    
    if any(word in time_lower for word in ['pre', 'before', 'am']):
        return "Pre-market"
    elif any(word in time_lower for word in ['after', 'close', 'pm']):
        return "After-hours"
    elif any(word in time_lower for word in ['during', 'market', 'open']):
        return "Market hours"
    else:
        return "Unknown"

def format_currency(amount: float, currency: str = 'USD') -> str:
    """
    Format currency amounts
    """
    if pd.isna(amount):
        return ""
    
    if currency == 'USD':
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def calculate_days_until(target_date) -> int:
    """
    Calculate days until target date
    """
    if pd.isna(target_date):
        return -1
    
    try:
        if isinstance(target_date, str):
            target_date = pd.to_datetime(target_date)
        
        today = datetime.now().date()
        if hasattr(target_date, 'date'):
            target_date = target_date.date()
        
        return (target_date - today).days
    except:
        return -1

def get_quarter_from_date(date_obj) -> str:
    """
    Get quarter from date (Q1, Q2, Q3, Q4)
    """
    if pd.isna(date_obj):
        return ""
    
    try:
        if isinstance(date_obj, str):
            date_obj = pd.to_datetime(date_obj)
        
        month = date_obj.month
        year = date_obj.year
        
        if month in [1, 2, 3]:
            return f"Q1 {year}"
        elif month in [4, 5, 6]:
            return f"Q2 {year}"
        elif month in [7, 8, 9]:
            return f"Q3 {year}"
        else:
            return f"Q4 {year}"
    except:
        return ""

def create_backup_file(df: pd.DataFrame, filename: str):
    """
    Create backup file of earnings data
    """
    try:
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f"{filename}_{timestamp}.csv")
        
        df.to_csv(backup_path, index=False)
        return backup_path
    except Exception as e:
        logging.error(f"Error creating backup: {e}")
        return None

def load_config():
    """
    Load configuration settings
    """
    default_config = {
        'refresh_interval': 3600,  # 1 hour
        'max_articles_per_ticker': 5,
        'max_days_back': 30,
        'enable_caching': True,
        'log_level': 'INFO'
    }
    
    # In a real implementation, this would load from a config file
    return default_config
