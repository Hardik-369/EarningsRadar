import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import logging
import time
import re
import json
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class EarningsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
    def get_earnings_calendar(self, days_ahead: int = 30) -> pd.DataFrame:
        """
        Scrape earnings calendar data from multiple sources
        """
        all_earnings = []
        
        # Try multiple sources for better data coverage
        sources = [
            self._scrape_finviz_earnings,
            self._scrape_investing_earnings,
            self._scrape_yahoo_finance_api,
            self._scrape_marketwatch_earnings
        ]
        
        for source_func in sources:
            try:
                earnings = source_func(days_ahead)
                if earnings:
                    all_earnings.extend(earnings)
                    logger.info(f"Successfully scraped {len(earnings)} earnings from {source_func.__name__}")
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Error scraping from {source_func.__name__}: {e}")
                continue
        
        if not all_earnings:
            logger.error("No earnings data scraped from any source")
            return pd.DataFrame()
        
        # Convert to DataFrame and remove duplicates
        df = pd.DataFrame(all_earnings)
        df = df.drop_duplicates(subset=['ticker', 'date'], keep='first')
        
        # Sort by date
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        
        return df
    
    def _scrape_finviz_earnings(self, days_ahead: int) -> List[Dict]:
        """
        Scrape earnings from Finviz earnings calendar
        """
        earnings = []
        
        try:
            url = "https://finviz.com/calendar.ashx"
            
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the earnings calendar table
            calendar_table = soup.find('table', {'class': 'calendar'})
            if not calendar_table:
                calendar_table = soup.find('table', {'bgcolor': '#d3d3d3'})
            
            if calendar_table:
                rows = calendar_table.find_all('tr')
                current_date = None
                
                for row in rows:
                    cells = row.find_all('td')
                    
                    # Check if this is a date header row
                    if len(cells) == 1 and cells[0].get('colspan'):
                        date_text = cells[0].get_text(strip=True)
                        current_date = self._parse_finviz_date(date_text)
                        continue
                    
                    # Process earnings row
                    if len(cells) >= 3 and current_date:
                        try:
                            ticker_elem = cells[1].find('a')
                            if ticker_elem:
                                ticker = ticker_elem.get_text(strip=True)
                                company = cells[2].get_text(strip=True)
                                time_str = cells[0].get_text(strip=True)
                                
                                if ticker and (current_date - datetime.now().date()).days <= days_ahead:
                                    earnings.append({
                                        'ticker': ticker,
                                        'company': company,
                                        'date': current_date,
                                        'time': time_str,
                                        'source': 'Finviz'
                                    })
                        except Exception as e:
                            logger.warning(f"Error parsing Finviz row: {e}")
                            continue
            
        except Exception as e:
            logger.error(f"Error scraping Finviz earnings: {e}")
        
        return earnings
    
    def _scrape_yahoo_finance_api(self, days_ahead: int) -> List[Dict]:
        """
        Scrape earnings using Yahoo Finance API approach
        """
        earnings = []
        
        try:
            # Yahoo Finance calendar endpoint
            today = datetime.now()
            end_date = today + timedelta(days=days_ahead)
            
            # Format dates for API
            start_timestamp = int(today.timestamp())
            end_timestamp = int(end_date.timestamp())
            
            url = f"https://finance.yahoo.com/calendar/earnings?from={today.strftime('%Y-%m-%d')}&to={end_date.strftime('%Y-%m-%d')}&day={today.strftime('%Y-%m-%d')}"
            
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for earnings data in script tags or table
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        try:
                            # Extract ticker from link
                            ticker_link = cells[0].find('a')
                            if ticker_link:
                                ticker = ticker_link.get_text(strip=True)
                                company = cells[1].get_text(strip=True)
                                
                                # Extract earnings time
                                time_str = "N/A"
                                if len(cells) > 2:
                                    time_str = cells[2].get_text(strip=True)
                                
                                # Use current date for now, improve date parsing later
                                earnings_date = today.date()
                                
                                if ticker and (earnings_date - datetime.now().date()).days <= days_ahead:
                                    earnings.append({
                                        'ticker': ticker,
                                        'company': company,
                                        'date': earnings_date,
                                        'time': time_str,
                                        'source': 'Yahoo Finance'
                                    })
                        except Exception as e:
                            logger.warning(f"Error parsing Yahoo Finance row: {e}")
                            continue
            
        except Exception as e:
            logger.error(f"Error scraping Yahoo Finance earnings: {e}")
        
        return earnings
    
    def _scrape_investing_earnings(self, days_ahead: int) -> List[Dict]:
        """
        Scrape earnings from Investing.com earnings calendar
        """
        earnings = []
        
        try:
            url = "https://www.investing.com/earnings-calendar/"
            
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the earnings calendar table
            calendar_table = soup.find('table', {'id': 'earningsCalendarData'})
            if not calendar_table:
                calendar_table = soup.find('table', {'class': 'genTbl'})
            
            if calendar_table:
                rows = calendar_table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        try:
                            # Extract company and ticker
                            company_cell = cells[1] if len(cells) > 1 else None
                            if company_cell:
                                company_link = company_cell.find('a')
                                if company_link:
                                    company = company_link.get_text(strip=True)
                                    
                                    # Try to extract ticker from title or data attributes
                                    ticker = company_link.get('title', '').split('(')[-1].replace(')', '') if '(' in company_link.get('title', '') else ''
                                    
                                    if not ticker:
                                        # Try to find ticker in nearby cells
                                        ticker_text = cells[0].get_text(strip=True) if cells else ''
                                        if ticker_text and len(ticker_text) <= 5:
                                            ticker = ticker_text
                                    
                                    # Extract time
                                    time_str = cells[2].get_text(strip=True) if len(cells) > 2 else 'N/A'
                                    
                                    # For now, use today's date - this should be improved
                                    earnings_date = datetime.now().date()
                                    
                                    if ticker and company:
                                        earnings.append({
                                            'ticker': ticker,
                                            'company': company,
                                            'date': earnings_date,
                                            'time': time_str,
                                            'source': 'Investing.com'
                                        })
                        except Exception as e:
                            logger.warning(f"Error parsing Investing.com row: {e}")
                            continue
            
        except Exception as e:
            logger.error(f"Error scraping Investing.com earnings: {e}")
        
        return earnings
    
    def _scrape_marketwatch_earnings(self, days_ahead: int) -> List[Dict]:
        """
        Scrape earnings from MarketWatch earnings calendar
        """
        earnings = []
        
        try:
            # MarketWatch earnings calendar
            url = "https://www.marketwatch.com/tools/earnings-calendar"
            
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for earnings table or list
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        try:
                            # Extract ticker and company
                            ticker_cell = cells[0] if cells else None
                            company_cell = cells[1] if len(cells) > 1 else None
                            
                            if ticker_cell and company_cell:
                                ticker_link = ticker_cell.find('a')
                                ticker = ticker_link.get_text(strip=True) if ticker_link else ticker_cell.get_text(strip=True)
                                company = company_cell.get_text(strip=True)
                                
                                # Extract time if available
                                time_str = cells[2].get_text(strip=True) if len(cells) > 2 else 'N/A'
                                
                                # Use current date for now
                                earnings_date = datetime.now().date()
                                
                                if ticker and company:
                                    earnings.append({
                                        'ticker': ticker,
                                        'company': company,
                                        'date': earnings_date,
                                        'time': time_str,
                                        'source': 'MarketWatch'
                                    })
                        except Exception as e:
                            logger.warning(f"Error parsing MarketWatch row: {e}")
                            continue
            
        except Exception as e:
            logger.error(f"Error scraping MarketWatch earnings: {e}")
        
        return earnings
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string into datetime object
        """
        try:
            # Clean the date string
            date_str = date_str.strip()
            
            # Common date formats
            formats = [
                '%Y-%m-%d',
                '%m/%d/%Y',
                '%m/%d/%y',
                '%b %d, %Y',
                '%B %d, %Y',
                '%d %b %Y',
                '%d %B %Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            
            # Try parsing relative dates
            if 'today' in date_str.lower():
                return datetime.now().date()
            elif 'tomorrow' in date_str.lower():
                return (datetime.now() + timedelta(days=1)).date()
            elif 'yesterday' in date_str.lower():
                return (datetime.now() - timedelta(days=1)).date()
            
        except Exception as e:
            logger.warning(f"Error parsing date '{date_str}': {e}")
        
        return None
    
    def _parse_finviz_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse Finviz date format
        """
        try:
            # Finviz uses formats like "Monday, February 5th"
            date_str = date_str.strip()
            
            # Remove ordinal suffixes (st, nd, rd, th)
            date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
            
            # Common Finviz date formats
            formats = [
                '%A, %B %d',
                '%B %d',
                '%m/%d/%Y',
                '%Y-%m-%d'
            ]
            
            current_year = datetime.now().year
            
            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    # If no year specified, use current year
                    if parsed_date.year == 1900:
                        parsed_date = parsed_date.replace(year=current_year)
                    return parsed_date.date()
                except ValueError:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error parsing Finviz date '{date_str}': {e}")
        
        return datetime.now().date()  # Fallback to today
    
    
    def __del__(self):
        """Close session when object is destroyed"""
        try:
            self.session.close()
        except:
            pass
