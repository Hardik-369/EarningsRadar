import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import logging

# Import custom modules
from earnings_scraper import EarningsScraper
from news_scraper import NewsScraper
from utils import format_date, export_to_csv, setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="EarningsRadar",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .earnings-card {
        background-color: #fff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .news-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #28a745;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_earnings_data():
    """Load earnings data with caching"""
    try:
        scraper = EarningsScraper()
        return scraper.get_earnings_calendar()
    except Exception as e:
        logger.error(f"Error loading earnings data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def load_news_data(tickers):
    """Load news data for given tickers"""
    try:
        news_scraper = NewsScraper()
        return news_scraper.get_news_for_tickers(tickers)
    except Exception as e:
        logger.error(f"Error loading news data: {e}")
        return pd.DataFrame()

def main():
    # Header
    st.markdown('<h1 class="main-header">📈 EarningsRadar</h1>', unsafe_allow_html=True)
    st.markdown("**Track upcoming earnings calls and stay updated with financial news**")
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Load data
    with st.spinner("Loading earnings data..."):
        earnings_df = load_earnings_data()
    
    if earnings_df.empty:
        st.error("Unable to load earnings data. Please check your connection and try again.")
        st.info("Possible reasons: Website changes, rate limiting, or connection issues.")
        st.stop()
    
    # Date range filter
    today = datetime.now().date()
    max_date = today + timedelta(days=30)
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(today, max_date),
        min_value=today,
        max_value=today + timedelta(days=90)
    )
    
    # Ticker filter
    available_tickers = sorted(earnings_df['ticker'].unique())
    
    # Primary ticker selection
    ticker_selection_mode = st.sidebar.radio(
        "Ticker Selection Mode",
        ["All Tickers", "Single Ticker", "Multiple Tickers", "Popular Tickers"],
        index=0
    )
    
    if ticker_selection_mode == "All Tickers":
        selected_tickers = available_tickers
        st.sidebar.info(f"Showing all {len(available_tickers)} tickers")
        
    elif ticker_selection_mode == "Single Ticker":
        # Add search functionality for single ticker
        ticker_search = st.sidebar.text_input(
            "Search Ticker (optional)",
            placeholder="Type to filter tickers..."
        )
        
        # Filter tickers based on search
        if ticker_search:
            filtered_tickers = [t for t in available_tickers if ticker_search.upper() in t.upper()]
            if not filtered_tickers:
                st.sidebar.warning(f"No tickers found matching '{ticker_search}'")
                filtered_tickers = available_tickers
        else:
            filtered_tickers = available_tickers
        
        selected_ticker = st.sidebar.selectbox(
            "Choose a Ticker",
            filtered_tickers,
            index=0
        )
        selected_tickers = [selected_ticker]
        
    elif ticker_selection_mode == "Multiple Tickers":
        # Add search functionality for multiple tickers
        multi_ticker_search = st.sidebar.text_input(
            "Search Tickers (optional)",
            placeholder="Type to filter tickers...",
            key="multi_search"
        )
        
        # Filter tickers based on search
        if multi_ticker_search:
            filtered_multi_tickers = [t for t in available_tickers if multi_ticker_search.upper() in t.upper()]
            if not filtered_multi_tickers:
                st.sidebar.warning(f"No tickers found matching '{multi_ticker_search}'")
                filtered_multi_tickers = available_tickers
        else:
            filtered_multi_tickers = available_tickers
        
        selected_tickers = st.sidebar.multiselect(
            "Choose Multiple Tickers",
            filtered_multi_tickers,
            default=filtered_multi_tickers[:5] if len(filtered_multi_tickers) >= 5 else filtered_multi_tickers[:3]
        )
        
    elif ticker_selection_mode == "Popular Tickers":
        # Popular tickers that are commonly followed
        popular_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'DIS', 'PYPL']
        
        # Filter to only include popular tickers that are available
        available_popular = [t for t in popular_tickers if t in available_tickers]
        
        if available_popular:
            selected_tickers = st.sidebar.multiselect(
                "Popular Tickers with Earnings",
                available_popular,
                default=available_popular
            )
            
            st.sidebar.info(f"Showing {len(available_popular)} popular tickers with upcoming earnings")
        else:
            st.sidebar.warning("No popular tickers found in current earnings data")
            selected_tickers = available_tickers[:10]  # Fallback to first 10
    
    else:
        # Fallback case
        selected_tickers = available_tickers
    
    # Company name filter
    company_search = st.sidebar.text_input("Search Company Name")
    
    # Filter earnings data
    filtered_df = earnings_df.copy()
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['date'].dt.date >= date_range[0]) & 
            (filtered_df['date'].dt.date <= date_range[1])
        ]
    
    if selected_tickers:
        filtered_df = filtered_df[filtered_df['ticker'].isin(selected_tickers)]
    
    if company_search:
        filtered_df = filtered_df[
            filtered_df['company'].str.contains(company_search, case=False, na=False)
        ]
    
    # Show current selection info
    if ticker_selection_mode == "All Tickers":
        st.info(f"📊 Showing data for **all {len(selected_tickers)} tickers**")
    elif ticker_selection_mode == "Single Ticker":
        if selected_tickers:
            st.info(f"📊 Showing data for ticker: **{selected_tickers[0]}**")
        else:
            st.warning("⚠️ No ticker selected.")
    elif ticker_selection_mode == "Popular Tickers":
        if selected_tickers:
            st.info(f"⭐ Showing data for **{len(selected_tickers)} popular tickers**: {', '.join(selected_tickers[:5])}{'...' if len(selected_tickers) > 5 else ''}")
        else:
            st.warning("⚠️ No popular tickers selected.")
    else:  # Multiple Tickers
        if selected_tickers:
            st.info(f"📊 Showing data for **{len(selected_tickers)} selected tickers**: {', '.join(selected_tickers[:5])}{'...' if len(selected_tickers) > 5 else ''}")
        else:
            st.warning("⚠️ No tickers selected. Please select at least one ticker.")
    
    # Main content
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Earnings", len(filtered_df))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        today_count = len(filtered_df[filtered_df['date'].dt.date == today])
        st.metric("Today's Earnings", today_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        week_count = len(filtered_df[filtered_df['date'].dt.date <= today + timedelta(days=7)])
        st.metric("This Week", week_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        unique_companies = filtered_df['ticker'].nunique()
        st.metric("Unique Companies", unique_companies)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Calendar View", "📊 Table View", "📰 News", "📈 Analytics"])
    
    with tab1:
        st.subheader("Earnings Calendar")
        
        # Calendar visualization
        if not filtered_df.empty:
            fig = px.timeline(
                filtered_df, 
                x_start="date", 
                x_end="date",
                y="ticker",
                title="Upcoming Earnings Timeline",
                color="ticker",
                hover_data=["company", "time"],
                height=600
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No earnings data available for selected filters.")
    
    with tab2:
        st.subheader("Earnings Schedule")
        
        if not filtered_df.empty:
            # Display table
            display_df = filtered_df.copy()
            display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
            display_df = display_df.rename(columns={
                'company': 'Company',
                'ticker': 'Ticker',
                'date': 'Date',
                'time': 'Time'
            })
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Export functionality
            if st.button("📥 Export to CSV"):
                csv_data = export_to_csv(filtered_df)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"earnings_calendar_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No earnings data available for selected filters.")
    
    with tab3:
        st.subheader("Financial News")
        
        if selected_tickers:
            with st.spinner("Loading news articles..."):
                news_df = load_news_data(selected_tickers[:5])  # Limit to 5 tickers for performance
            
            if not news_df.empty:
                for _, article in news_df.iterrows():
                    st.markdown(f'<div class="news-card">', unsafe_allow_html=True)
                    st.markdown(f"**{article['title']}**")
                    st.markdown(f"*{article['ticker']} - {article['date']}*")
                    st.markdown(f"{article['summary']}")
                    if article['url']:
                        st.markdown(f"[Read more]({article['url']})")
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No news articles found for selected tickers.")
        else:
            st.info("Please select tickers to load news articles.")
    
    with tab4:
        st.subheader("Analytics")
        
        if not filtered_df.empty:
            # Earnings by day of week
            filtered_df['day_of_week'] = filtered_df['date'].dt.day_name()
            day_counts = filtered_df['day_of_week'].value_counts()
            
            fig1 = px.bar(
                x=day_counts.index,
                y=day_counts.values,
                title="Earnings by Day of Week",
                labels={'x': 'Day of Week', 'y': 'Count'}
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Earnings by date
            date_counts = filtered_df.groupby(filtered_df['date'].dt.date).size()
            
            fig2 = px.line(
                x=date_counts.index,
                y=date_counts.values,
                title="Earnings Count by Date",
                labels={'x': 'Date', 'y': 'Count'}
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No data available for analytics.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**EarningsRadar** | Data refreshed every hour | "
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

if __name__ == "__main__":
    main()
