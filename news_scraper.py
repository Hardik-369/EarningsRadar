import requests
from newspaper import Article
import pandas as pd
from datetime import datetime, timedelta
import logging
import time
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_news_for_tickers(self, tickers: List[str], days_back: int = 7) -> pd.DataFrame:
        """
        Get news articles for specified tickers
        """
        all_articles = []
        
        for ticker in tickers:
            try:
                articles = self._get_ticker_news(ticker, days_back)
                all_articles.extend(articles)
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Error getting news for {ticker}: {e}")
                continue
        
        if not all_articles:
            logger.warning("No news articles scraped from any source")
            return pd.DataFrame()
        
        # Convert to DataFrame and remove duplicates
        df = pd.DataFrame(all_articles)
        df = df.drop_duplicates(subset=['url'], keep='first')
        
        # Sort by date (newest first)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date', ascending=False).reset_index(drop=True)
        
        return df
    
    def _get_ticker_news(self, ticker: str, days_back: int) -> List[Dict]:
        """
        Get news articles for a specific ticker from multiple sources
        """
        articles = []
        
        # Try multiple news sources
        sources = [
            self._get_yahoo_news,
            self._get_marketwatch_news,
            self._get_google_news
        ]
        
        for source_func in sources:
            try:
                source_articles = source_func(ticker, days_back)
                articles.extend(source_articles)
            except Exception as e:
                logger.warning(f"Error getting news from {source_func.__name__} for {ticker}: {e}")
                continue
        
        return articles
    
    def _get_yahoo_news(self, ticker: str, days_back: int) -> List[Dict]:
        """
        Get news articles from Yahoo Finance
        """
        articles = []
        
        try:
            url = f"https://finance.yahoo.com/quote/{ticker}/news"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find news articles
            news_items = soup.find_all('div', {'class': 'Ov(h) Pend(14px) Pstart(14px)'})
            
            for item in news_items[:5]:  # Limit to 5 articles per ticker
                try:
                    # Extract article link
                    link_elem = item.find('a')
                    if not link_elem:
                        continue
                    
                    article_url = link_elem.get('href')
                    if article_url and article_url.startswith('/'):
                        article_url = f"https://finance.yahoo.com{article_url}"
                    
                    # Extract title
                    title_elem = item.find('h3') or item.find('h2')
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    
                    # Extract date
                    date_elem = item.find('span', {'class': 'C(#959595)'})
                    date_str = date_elem.get_text(strip=True) if date_elem else ""
                    
                    if title and article_url:
                        # Parse the full article for summary
                        article_data = self._parse_article(article_url)
                        
                        articles.append({
                            'ticker': ticker,
                            'title': title,
                            'url': article_url,
                            'date': self._parse_news_date(date_str),
                            'summary': article_data.get('summary', ''),
                            'full_text': article_data.get('text', ''),
                            'source': 'Yahoo Finance'
                        })
                        
                except Exception as e:
                    logger.warning(f"Error parsing Yahoo article: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error getting Yahoo news for {ticker}: {e}")
        
        return articles
    
    def _get_marketwatch_news(self, ticker: str, days_back: int) -> List[Dict]:
        """
        Get news articles from MarketWatch
        """
        articles = []
        
        try:
            url = f"https://www.marketwatch.com/investing/stock/{ticker}/news"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find news articles
            news_items = soup.find_all('div', {'class': 'article__content'})
            
            for item in news_items[:5]:  # Limit to 5 articles per ticker
                try:
                    # Extract article link
                    link_elem = item.find('a', {'class': 'link'})
                    if not link_elem:
                        continue
                    
                    article_url = link_elem.get('href')
                    if article_url and not article_url.startswith('http'):
                        article_url = f"https://www.marketwatch.com{article_url}"
                    
                    # Extract title
                    title = link_elem.get_text(strip=True)
                    
                    # Extract date
                    date_elem = item.find('span', {'class': 'article__timestamp'})
                    date_str = date_elem.get_text(strip=True) if date_elem else ""
                    
                    if title and article_url:
                        # Parse the full article for summary
                        article_data = self._parse_article(article_url)
                        
                        articles.append({
                            'ticker': ticker,
                            'title': title,
                            'url': article_url,
                            'date': self._parse_news_date(date_str),
                            'summary': article_data.get('summary', ''),
                            'full_text': article_data.get('text', ''),
                            'source': 'MarketWatch'
                        })
                        
                except Exception as e:
                    logger.warning(f"Error parsing MarketWatch article: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error getting MarketWatch news for {ticker}: {e}")
        
        return articles
    
    def _get_google_news(self, ticker: str, days_back: int) -> List[Dict]:
        """
        Get news articles from Google News search
        """
        articles = []
        
        try:
            # Search for ticker-related news
            query = f"{ticker} stock earnings financial news"
            url = f"https://news.google.com/rss/search?q={query}"
            
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'xml')
            
            # Parse RSS feed
            items = soup.find_all('item')
            
            for item in items[:3]:  # Limit to 3 articles per ticker
                try:
                    title = item.find('title').get_text(strip=True)
                    link = item.find('link').get_text(strip=True)
                    pub_date = item.find('pubDate').get_text(strip=True)
                    
                    # Skip if article is too old
                    article_date = self._parse_news_date(pub_date)
                    if article_date and (datetime.now() - article_date).days > days_back:
                        continue
                    
                    # Parse the full article for summary
                    article_data = self._parse_article(link)
                    
                    articles.append({
                        'ticker': ticker,
                        'title': title,
                        'url': link,
                        'date': article_date,
                        'summary': article_data.get('summary', ''),
                        'full_text': article_data.get('text', ''),
                        'source': 'Google News'
                    })
                    
                except Exception as e:
                    logger.warning(f"Error parsing Google News article: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error getting Google News for {ticker}: {e}")
        
        return articles
    
    def _parse_article(self, url: str) -> Dict[str, str]:
        """
        Parse article content using newspaper3k
        """
        try:
            article = Article(url)
            article.download()
            article.parse()
            article.nlp()
            
            return {
                'text': article.text,
                'summary': article.summary,
                'authors': article.authors,
                'publish_date': article.publish_date
            }
            
        except Exception as e:
            logger.warning(f"Error parsing article {url}: {e}")
            return {
                'text': '',
                'summary': '',
                'authors': [],
                'publish_date': None
            }
    
    def _parse_news_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse news date string into datetime object
        """
        if not date_str:
            return datetime.now()
        
        try:
            # Clean the date string
            date_str = date_str.strip()
            
            # Common date formats in news
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%m/%d/%Y %H:%M:%S',
                '%m/%d/%Y',
                '%b %d, %Y %H:%M:%S',
                '%B %d, %Y %H:%M:%S',
                '%b %d, %Y',
                '%B %d, %Y',
                '%a, %d %b %Y %H:%M:%S %Z',  # RSS format
                '%a, %d %b %Y %H:%M:%S %z'   # RSS format with timezone
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # Try parsing relative dates
            if 'hour' in date_str.lower():
                hours = int(re.search(r'(\d+)', date_str).group(1))
                return datetime.now() - timedelta(hours=hours)
            elif 'day' in date_str.lower():
                days = int(re.search(r'(\d+)', date_str).group(1))
                return datetime.now() - timedelta(days=days)
            elif 'minute' in date_str.lower():
                minutes = int(re.search(r'(\d+)', date_str).group(1))
                return datetime.now() - timedelta(minutes=minutes)
            
        except Exception as e:
            logger.warning(f"Error parsing news date '{date_str}': {e}")
        
        return datetime.now()
    
