# EarningsRadar 📈

A powerful Streamlit web application that scrapes and displays real-time upcoming public company earnings call dates along with recent financial news articles. Track earnings across multiple companies with advanced filtering and selection options.

## ✨ Key Features

### 📊 Real-Time Data Scraping
- **Multi-Source Earnings Data**: Scrapes from Finviz, Investing.com, Yahoo Finance, and MarketWatch
- **Live Financial News**: Fetches and summarizes recent news articles using newspaper3k
- **No Sample Data**: 100% real-time data with robust error handling

### 🎯 Advanced Ticker Selection
- **4 Selection Modes**: All Tickers, Single Ticker, Multiple Tickers, Popular Tickers
- **Smart Search**: Real-time filtering with case-insensitive search
- **Popular Stocks**: Quick access to major companies (AAPL, MSFT, GOOGL, etc.)
- **Visual Feedback**: Real-time selection info and status updates

### 📱 Interactive Dashboard
- **Multiple Views**: Calendar timeline, sortable table, news feed, and analytics
- **Export Options**: Download earnings data as CSV or iCalendar format
- **Responsive Design**: Clean, minimal UI optimized for all screen sizes
- **Error Handling**: Graceful fallbacks and user-friendly error messages

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Internet connection for real-time data scraping

### Installation

1. **Clone or download** this repository:
   ```bash
   git clone https://github.com/your-repo/earnings-radar.git
   cd earnings-radar
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** to `http://localhost:8501`

### 📦 Dependencies

- **streamlit**: Web application framework
- **requests**: HTTP library for web scraping
- **beautifulsoup4**: HTML parsing and web scraping
- **newspaper3k**: News article parsing and summarization
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive charts and visualizations
- **python-dateutil**: Advanced date parsing

## 📱 How to Use

### 🎯 Ticker Selection (New!)

Choose from **4 powerful selection modes** in the sidebar:

#### 1. 📊 **All Tickers Mode** (Default)
- View all available companies with upcoming earnings
- Perfect for getting a comprehensive market overview
- Shows total count of available tickers

#### 2. 🎯 **Single Ticker Mode**
- Focus on one specific company
- **Search feature**: Type to filter available tickers
- **Smart dropdown**: Select from filtered results
- Ideal for deep-dive analysis of individual companies

#### 3. ✅ **Multiple Tickers Mode**
- Compare earnings across several chosen companies
- **Search functionality**: Filter tickers as you type
- **Multi-select**: Choose multiple companies simultaneously
- **Smart defaults**: Pre-selects top companies for quick start

#### 4. ⭐ **Popular Tickers Mode**
- Quick access to major stocks (AAPL, MSFT, GOOGL, AMZN, TSLA, etc.)
- **Pre-filtered list**: Only shows popular tickers with upcoming earnings
- **Auto-selection**: All available popular tickers selected by default
- Perfect for tracking major market movers

### 📊 Additional Filters

- **📅 Date Range**: Select start and end dates (up to 90 days)
- **🔍 Company Search**: Search by company name across all data
- **⚙️ Real-time Updates**: Data refreshes automatically

### 📈 Dashboard Views

1. **📅 Calendar View**: Interactive timeline visualization of upcoming earnings
2. **📊 Table View**: Sortable table with company details and export functionality
3. **📰 News Feed**: Recent financial news articles for selected tickers
4. **📈 Analytics**: Charts showing earnings patterns and trends

### 💾 Export Options

- **📊 CSV Export**: Download filtered earnings data for external analysis
- **📅 iCalendar**: Add earnings events directly to your calendar app
- **🗒️ Backup**: Automatic data backup functionality

## 🌐 Data Sources

EarningsRadar scrapes **real-time data** from multiple reliable sources:

### 📊 Earnings Data
- **💹 Finviz**: Comprehensive earnings calendar with detailed formatting
- **🌎 Investing.com**: International earnings data and market coverage
- **💰 Yahoo Finance**: Real-time earnings calendar and company information
- **📰 MarketWatch**: Financial news and earnings schedule integration

### 📰 News Sources
- **Yahoo Finance News**: Company-specific financial news and analyst reports
- **MarketWatch Articles**: Market analysis and earnings-related coverage
- **Google News RSS**: Aggregated financial news from multiple publishers
- **Real-time Parsing**: Uses newspaper3k for article summarization

## ⚙️ Configuration

### 📏 Real-Time Data Only
- **No Sample Data**: 100% live data scraping with robust error handling
- **Multi-Source Redundancy**: If one source fails, others provide backup
- **Smart Fallbacks**: Graceful degradation when sources are unavailable

### 🚀 Performance Optimization
- **💾 Intelligent Caching**: 
  - Earnings data cached for 1 hour
  - News data cached for 30 minutes
  - Reduces API calls and improves speed
- **⌚ Rate Limiting**: Built-in delays to respect website limits
- **📊 Efficient Filtering**: Client-side filtering for responsive UI

### 📋 Logging & Monitoring
- **Detailed Logs**: Saved to `earnings_radar.log` for debugging
- **Error Tracking**: Comprehensive error handling and reporting
- **Source Monitoring**: Tracks success/failure rates for each data source

## 📁 Project Structure

```
EarningsRadar/
├── app.py                           # 📱 Main Streamlit application
├── earnings_scraper.py              # 📊 Real-time earnings data scraper
├── news_scraper.py                  # 📰 Financial news article scraper
├── utils.py                        # 🔧 Utility functions and helpers
├── requirements.txt                # 📦 Python dependencies
├── test_app.py                     # 🧪 Test suite for all components
├── README.md                       # 📝 This documentation
├── TICKER_SELECTION_FEATURES.md    # 🎯 Detailed ticker selection guide
└── earnings_radar.log              # 📋 Application logs (auto-created)
```

## 🧪 Testing

Run the comprehensive test suite to verify all components:

```bash
python test_app.py
```

The test suite validates:
- ✅ **Dependencies**: All required packages are installed
- ✅ **Utilities**: Date formatting, ticker validation, CSV export
- ✅ **Earnings Scraper**: Real-time data collection from multiple sources
- ✅ **News Scraper**: Financial news fetching and parsing

## 🔍 Quick Demo

To see real-time data in action:

1. **Check Dependencies**: `python test_app.py`
2. **Start the App**: `streamlit run app.py`
3. **Open Browser**: Navigate to `http://localhost:8501`
4. **Try Different Modes**: Test all 4 ticker selection options
5. **Explore Views**: Calendar, Table, News, and Analytics tabs

## 🚀 Performance Features

### 🔍 Smart Error Handling
- **🔄 Multi-Source Redundancy**: If one source fails, others continue working
- **🛡️ Graceful Degradation**: App continues functioning with partial data
- **📝 Detailed Logging**: All errors logged for debugging and monitoring
- **🚨 User Notifications**: Clear, actionable error messages for users

### ⚡ Optimization Techniques
- **💾 Smart Caching**: Streamlit's `@st.cache_data` for efficient data loading
- **⌚ Rate Limiting**: Controlled request frequency to respect website limits
- **📊 Client-Side Filtering**: Real-time filtering without server round-trips
- **🔄 Lazy Loading**: News articles loaded only when tabs are accessed
- **📚 Memory Management**: Efficient data structures and cleanup

## 🚑 Troubleshooting

### 🔴 Common Issues & Solutions

#### 1. 🐌 **Slow Loading Times**
**Symptoms**: App takes long to load data
**Solutions**:
- ✓ Check internet connection stability
- ✓ Wait for loading spinners to complete
- ✓ Try different ticker selection modes
- ✓ Some financial websites may have high response times

#### 2. 📯 **No Earnings Data Displayed**
**Symptoms**: "Unable to load earnings data" error
**Solutions**:
- ✓ Verify internet connection
- ✓ Check `earnings_radar.log` for specific errors
- ✓ Financial websites may be temporarily unavailable
- ✓ Try refreshing the app (Ctrl+R)

#### 3. 📦 **Package Import Errors**
**Symptoms**: ModuleNotFoundError or ImportError
**Solutions**:
```bash
# Reinstall all dependencies
pip install -r requirements.txt

# Check Python version (3.7+ required)
python --version

# Test individual components
python test_app.py
```

#### 4. 📰 **Limited News Articles**
**Symptoms**: Few or no news articles displayed
**Solutions**:
- ✓ This is normal - not all tickers have recent news
- ✓ Try Popular Tickers mode for better news coverage
- ✓ Select different date ranges

### 🔍 Debug Mode

Enable detailed logging for troubleshooting:

1. **Edit `utils.py`**:
   ```python
   logging.basicConfig(level=logging.DEBUG, ...)
   ```

2. **Run with verbose output**:
   ```bash
   streamlit run app.py --logger.level=debug
   ```

3. **Check log file**: View `earnings_radar.log` for detailed error information

### 🌐 Website Compatibility

**Note**: This app scrapes public financial websites. Occasional failures are normal due to:
- Website layout changes
- Anti-scraping measures
- Rate limiting
- Temporary server issues

The app is designed with redundancy to handle these situations gracefully.

## 🔧 Customization

### 🔌 Adding New Data Sources

Extend the app with additional earnings sources:

```python
# In earnings_scraper.py
def _scrape_new_source(self, days_ahead: int) -> List[Dict]:
    # Implement your scraping logic
    pass

# Add to sources list in get_earnings_calendar()
sources = [
    self._scrape_finviz_earnings,
    self._scrape_investing_earnings,
    self._scrape_your_new_source  # Add here
]
```

### 🎨 UI Customization

Customize the app appearance by modifying the CSS in `app.py`:

```python
# Update the st.markdown() CSS section
st.markdown("""
<style>
    .main-header {
        color: #your-color;  # Customize colors
        font-size: 3rem;    # Adjust sizes
    }
</style>
""", unsafe_allow_html=True)
```

### ⚙️ Configuration Options

Modify `utils.py` to add new settings:

```python
def load_config():
    return {
        'refresh_interval': 3600,  # Adjust refresh rate
        'max_articles_per_ticker': 10,  # More news articles
        'enable_notifications': True,   # Add new features
    }
```

## ⚖️ Legal & Ethical Use

### 📜 Compliance Guidelines

✅ **Acceptable Use**:
- Educational and personal research
- Non-commercial analysis and learning
- Respect for website rate limits
- Compliance with robots.txt files

❌ **Prohibited Use**:
- Commercial redistribution of scraped data
- Overloading servers with excessive requests
- Circumventing anti-scraping measures
- Violating website terms of service

### 🛡️ Built-in Protections
- **Rate Limiting**: Automatic delays between requests
- **Respectful Scraping**: Follows best practices for web scraping
- **Error Handling**: Graceful failure without overwhelming servers
- **User-Agent Headers**: Proper identification in requests

## 🚀 Future Roadmap

### 🎆 Planned Features
- 🔔 **Real-time Notifications**: Email/SMS alerts for earnings
- 📱 **Mobile App**: React Native companion app
- 🤖 **AI Integration**: Sentiment analysis and predictions
- 📈 **Advanced Analytics**: Technical indicators and trends
- 🔗 **API Integration**: Direct broker/trading platform connections

### 📈 Enhancement Ideas
- **Watchlists**: Save and manage custom ticker lists
- **Portfolio Tracking**: Monitor your holdings' earnings
- **Sector Analysis**: Industry-wide earnings patterns
- **International Markets**: Global earnings coverage
- **Social Sentiment**: Twitter/Reddit sentiment integration

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 🐛 Bug Reports
1. Check existing issues first
2. Provide detailed reproduction steps
3. Include log files and screenshots
4. Specify your environment (OS, Python version)

### ✨ Feature Requests
1. Describe the feature and use case
2. Explain the expected behavior
3. Consider implementation complexity
4. Check if it aligns with project goals

### 💻 Code Contributions
1. Fork the repository
2. Create a feature branch
3. Follow existing code style
4. Add tests for new functionality
5. Submit a pull request

## 📜 License

This project is open-source and available under the MIT License. Feel free to use, modify, and distribute according to the license terms.

## 🖊️ Support

- 💬 **Issues**: GitHub Issues for bug reports and feature requests
- 📚 **Documentation**: This README and inline code comments
- 🧪 **Testing**: Comprehensive test suite included

---

## ⚠️ Important Disclaimer

**Educational Purpose**: This application is designed for educational and personal use only. 

**Data Accuracy**: Scraped data may not always be 100% accurate or complete. Always verify important information with official sources.

**Website Compliance**: Users are responsible for ensuring compliance with all applicable website terms of service and local laws.

**No Financial Advice**: This tool provides information only and should not be considered financial advice. Always consult with qualified financial professionals for investment decisions.

**Use at Your Own Risk**: The developers assume no responsibility for any decisions made based on data provided by this application.

---

🎉 **Happy Earnings Tracking!** 📈
