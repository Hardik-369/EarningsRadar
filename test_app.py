#!/usr/bin/env python3
"""
Test script for EarningsRadar application
"""

import sys
import pandas as pd
from datetime import datetime
import logging

# Configure logging for testing
logging.basicConfig(level=logging.INFO)

def test_earnings_scraper():
    """Test the earnings scraper"""
    print("Testing EarningsScraper...")
    
    try:
        from earnings_scraper import EarningsScraper
        
        scraper = EarningsScraper()
        
        # Test actual scraping
        earnings_df = scraper.get_earnings_calendar()
        print(f"✓ Earnings calendar: {len(earnings_df)} entries")
        
        if not earnings_df.empty:
            print(f"  Columns: {list(earnings_df.columns)}")
            print(f"  Date range: {earnings_df['date'].min()} to {earnings_df['date'].max()}")
            print(f"  Companies: {earnings_df['ticker'].head().tolist()}")
        else:
            print("  No earnings data available")
        
        return True
        
    except Exception as e:
        print(f"✗ EarningsScraper test failed: {e}")
        return False

def test_news_scraper():
    """Test the news scraper"""
    print("\nTesting NewsScraper...")
    
    try:
        from news_scraper import NewsScraper
        
        scraper = NewsScraper()
        
        # Test actual news scraping
        test_tickers = ['AAPL', 'MSFT']
        news_df = scraper.get_news_for_tickers(test_tickers)
        print(f"✓ News articles: {len(news_df)} entries")
        
        if not news_df.empty:
            print(f"  Columns: {list(news_df.columns)}")
            print(f"  Sample titles: {news_df['title'].head(2).tolist()}")
        else:
            print("  No news articles available")
        
        return True
        
    except Exception as e:
        print(f"✗ NewsScraper test failed: {e}")
        return False

def test_utils():
    """Test utility functions"""
    print("\nTesting utils...")
    
    try:
        from utils import (
            format_date, clean_ticker, validate_ticker, 
            get_earnings_time_category, export_to_csv
        )
        
        # Test date formatting
        test_date = datetime.now()
        formatted = format_date(test_date)
        print(f"✓ Date formatting: {formatted}")
        
        # Test ticker cleaning
        test_tickers = ['AAPL.US', 'msft-usd', 'GOOGL']
        for ticker in test_tickers:
            cleaned = clean_ticker(ticker)
            valid = validate_ticker(cleaned)
            print(f"✓ Ticker '{ticker}' -> '{cleaned}' (valid: {valid})")
        
        # Test time categorization
        test_times = ['Pre-market', 'After-hours', 'During market', 'Unknown']
        for time_str in test_times:
            category = get_earnings_time_category(time_str)
            print(f"✓ Time '{time_str}' -> '{category}'")
        
        # Test CSV export
        test_df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        csv_data = export_to_csv(test_df)
        print(f"✓ CSV export: {len(csv_data)} characters")
        
        return True
        
    except Exception as e:
        print(f"✗ Utils test failed: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available"""
    print("\nTesting dependencies...")
    
    required_modules = [
        'streamlit',
        'pandas',
        'requests',
        'bs4',
        'newspaper',
        'plotly'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"✗ {module} - NOT FOUND")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\nMissing modules: {missing_modules}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("EarningsRadar Application Tests")
    print("=" * 50)
    
    tests = [
        test_dependencies,
        test_utils,
        test_earnings_scraper,
        test_news_scraper
    ]
    
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! You can run the app with:")
        print("   streamlit run app.py")
    else:
        print("❌ Some tests failed. Check the output above for details.")
        print("   Try installing dependencies: pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
