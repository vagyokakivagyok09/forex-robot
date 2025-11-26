Çg"""
TTM Squeeze Trading Dashboard

Real-time forex monitoring with TTM Squeeze indicator
Premium dark mode design with Streamlit
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime
import plotly.graph_objects as go

# Import custom modules
from ttm_squeeze import calculate_ttm_squeeze, check_signal, get_squeeze_status
from data_fetcher import get_all_pairs_data, FOREX_PAIRS
from telegram_notifier import TelegramNotifier
import config


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="TTM Squeeze Dashboard",
    page_icon="üìä",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================

def load_custom_css():
    """Load custom CSS for professional forex trading design"""
    st.markdown("""
    <style>
    /* Main theme - Clean white with subtle pattern */
    .stApp {
        background: linear-gradient(to bottom, #ffffff 0%, #f8f9fa 100%);
        background-image: 
            linear-gradient(to bottom, #ffffff 0%, #f8f9fa 100%),
            repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(218, 165, 32, 0.03) 10px, rgba(218, 165, 32, 0.03) 20px);
    }
    
    /* Header styling - Forex gold theme */
    h1 {
        color: #1a1a1a;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        border-bottom: 3px solid #DAA520;
        padding-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    h2, h3 {
        color: #2c3e50;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    
    /* Card styling - Professional white cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        border: 2px solid #e8e8e8;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Table styling */
    .dataframe {
        background: white !important;
        border-radius: 8px;
        border: 1px solid #ddd;
    }
    
    /* Status badges - Trading colors */
    .status-squeeze-on {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(40, 167, 69, 0.3);
    }
    
    .status-squeeze-off {
        background: linear-gradient(135deg, #dc3545 0%, #c92333 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(220, 53, 69, 0.3);
    }
    
    .status-buy {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: 800;
        font-size: 16px;
        display: inline-block;
        animation: pulse 2s infinite;
        box-shadow: 0 4px 8px rgba(40, 167, 69, 0.4);
        border: 2px solid #1e7e34;
    }
    
    .status-sell {
        background: linear-gradient(135deg, #dc3545 0%, #c92333 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: 800;
        font-size: 16px;
        display: inline-block;
        animation: pulse 2s infinite;
        box-shadow: 0 4px 8px rgba(220, 53, 69, 0.4);
        border: 2px solid #bd2130;
    }
    
    .status-wait {
        background: #6c757d;
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: 600;
        display: inline-block;
    }
    
    @keyframes pulse {
        0%, 100% { 
            opacity: 1; 
            transform: scale(1);
        }
        50% { 
            opacity: 0.85;
            transform: scale(1.05);
        }
    }
    
    /* Sidebar styling - Professional gray */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
        color: white;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    /* Metrics - Forex themed cards */
    .stMetric {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #DAA520;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    .stMetric label {
        color: #2c3e50 !important;
        font-weight: 600;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #1a1a1a !important;
        font-weight: 800;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #DAA520 0%, #B8860B 100%);
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        box-shadow: 0 4px 6px rgba(218, 165, 32, 0.3);
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #B8860B 0%, #DAA520 100%);
        box-shadow: 0 6px 12px rgba(218, 165, 32, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_signal_badge(signal):
    """Format signal as HTML badge"""
    if signal == 'BUY':
        return '<span class="status-buy">üöÄ BUY</span>'
    elif signal == 'SELL':
        return '<span class="status-sell">üîª SELL</span>'
    else:
        return '<span class="status-wait">‚è∏Ô∏è WAIT</span>'


def format_squeeze_badge(squeeze_on):
    """Format squeeze status as HTML badge"""
    if squeeze_on:
        return '<span class="status-squeeze-on">üü¢ ON</span>'
    else:
        return '<span class="status-squeeze-off">üî¥ FIRE</span>'


def format_momentum_arrow(momentum):
    """Format momentum direction with arrow"""
    if momentum > 0:
        return f'‚ÜóÔ∏è {momentum:.5f}'
    elif momentum < 0:
        return f'‚ÜòÔ∏è {momentum:.5f}'
    else:
        return f'‚û°Ô∏è {momentum:.5f}'


def create_squeeze_chart(df, pair_name):
    """Create TTM Squeeze visualization chart"""
    fig = go.Figure()
    
    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price',
        increasing_line_color='#00ff88',
        decreasing_line_color='#ff3366'
    ))
    
    # Bollinger Bands
    fig.add_trace(go.Scatter(
        x=df.index, y=df['BB_Upper'],
        name='BB Upper',
        line=dict(color='rgba(0, 255, 136, 0.3)', width=1, dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['BB_Lower'],
        name='BB Lower',
        line=dict(color='rgba(0, 255, 136, 0.3)', width=1, dash='dash'),
        fill='tonexty',
        fillcolor='rgba(0, 255, 136, 0.05)'
    ))
    
    # Keltner Channels
    fig.add_trace(go.Scatter(
        x=df.index, y=df['KC_Upper'],
        name='KC Upper',
        line=dict(color='rgba(255, 51, 102, 0.5)', width=1)
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['KC_Lower'],
        name='KC Lower',
        line=dict(color='rgba(255, 51, 102, 0.5)', width=1)
    ))
    
    # Update layout
    fig.update_layout(
        title=f'{pair_name} - TTM Squeeze',
        template='plotly_dark',
        xaxis_title='Time',
        yaxis_title='Price',
        height=500,
        plot_bgcolor='rgba(0, 0, 0, 0.2)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(color='white')
    )
    
    return fig


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application function"""
    
    # Load custom CSS
    load_custom_css()
    
    # Header
    st.markdown("<h1>üìä TTM Squeeze Trading Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("**Real-time Forex Monitoring with Momentum Strategy**")
    st.markdown("---")
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### ‚öôÔ∏è Configuration")
        
        # Monitored pairs
        st.markdown(f"**Pairs:** {len(config.MONITORED_PAIRS)}")
        for pair in config.MONITORED_PAIRS:
            st.markdown(f"- {pair}")
        
        st.markdown("---")
        
        # Settings
        st.markdown(f"**Timeframe:** {config.DEFAULT_INTERVAL}")
        st.markdown(f"**BB Period:** {config.BB_PERIOD}")
        st.markdown(f"**KC Period:** {config.KC_PERIOD}")
        
        st.markdown("---")
        
        # Telegram status
        telegram_status = "üü¢ Enabled" if config.TELEGRAM_ENABLED else "üî¥ Disabled"
        st.markdown(f"**Telegram:** {telegram_status}")
        
        st.markdown("---")
        
        # Manual refresh button
        if st.button("üîÑ Refresh Now", use_container_width=True):
            st.rerun()
        
        # Auto-refresh info
        st.markdown(f"*Auto-refresh: {config.STREAMLIT_REFRESH_INTERVAL}s*")
    
    # Main content area
    with st.spinner('üìä Fetching market data...'):
        # Fetch data for all pairs
        data = get_all_pairs_data(
            pairs=config.MONITORED_PAIRS,
            interval=config.DEFAULT_INTERVAL,
            candles=config.CANDLES_TO_FETCH
        )
    
    if not data:
        st.error("‚ùå Failed to fetch market data. Please check your connection.")
        return
    
    # Process data and calculate indicators
    results = []
    
    for pair, df in data.items():
        if df.empty:
            continue
        
        # Calculate TTM Squeeze
        df_with_indicators = calculate_ttm_squeeze(
            df,
            bb_period=config.BB_PERIOD,
            bb_std=config.BB_STD_DEV,
            kc_period=config.KC_PERIOD,
            kc_atr_mult=config.KC_ATR_MULTIPLIER
        )
        
        # Get signal
        signal_info = check_signal(df_with_indicators)
        
        # Get current status
        status = get_squeeze_status(df_with_indicators)
        
        results.append({
            'Pair': pair,
            'Price': signal_info['price'],
            'Squeeze': status['squeeze_on'],
            'Momentum': status['momentum'],
            'Signal': signal_info['signal'],
            'df': df_with_indicators
        })
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("üìà Pairs Monitored", len(results))
    
    with col2:
        squeeze_on_count = sum(1 for r in results if r['Squeeze'])
        st.metric("üü¢ Squeeze ON", squeeze_on_count)
    
    with col3:
        buy_signals = sum(1 for r in results if r['Signal'] == 'BUY')
        st.metric("üöÄ BUY Signals", buy_signals)
    
    with col4:
        sell_signals = sum(1 for r in results if r['Signal'] == 'SELL')
        st.metric("üîª SELL Signals", sell_signals)
    
    st.markdown("---")
    
    # Display results table
    st.markdown("### üìä Market Overview")
    
    # Create display dataframe
    display_data = []
    for r in results:
        display_data.append({
            'Pair': r['Pair'],
            'Price': f"{r['Price']:.5f}",
            'Squeeze': format_squeeze_badge(r['Squeeze']),
            'Momentum': format_momentum_arrow(r['Momentum']),
            'Signal': format_signal_badge(r['Signal'])
        })
    
    df_display = pd.DataFrame(display_data)
    
    # Display as HTML table for custom styling
    st.markdown(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Detailed charts
    st.markdown("### üìà Detailed Charts")
    
    # Show charts for pairs with signals
    signal_pairs = [r for r in results if r['Signal'] != 'WAIT']
    
    if signal_pairs:
        for r in signal_pairs:
            with st.expander(f"üìä {r['Pair']} - {r['Signal']} Signal", expanded=True):
                fig = create_squeeze_chart(r['df'], r['Pair'])
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No active signals at the moment. Charts will appear when squeeze fires.")
    
    # Footer
    st.markdown("---")
    st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    st.markdown("*üí° Tip: Use the 'Refresh Now' button in the sidebar to update data*")


if __name__ == "__main__":
    main()
≠ *cascade08≠Ø*cascade08Ø∞ *cascade08∞≤*cascade08≤≥ *cascade08≥∑*cascade08∑∏ *cascade08∏∫*cascade08∫ª *cascade08ªΩ*cascade08Ωæ *cascade08æ¡*cascade08¡¬ *cascade08¬≈*cascade08≈Ö	 *cascade08Ö	ß	*cascade08ß	›	 *cascade08›	¸	*cascade08¸	˝	 *cascade08˝	ï
*cascade08ï
ñ
 *cascade08ñ
õ
*cascade08õ
ú
 *cascade08ú
≥
*cascade08≥
¥
 *cascade08¥
≈
*cascade08≈
»
 *cascade08»
œ
*cascade08œ
–
 *cascade08–
‘
*cascade08‘
’
 *cascade08’
◊
*cascade08◊
ÿ
 *cascade08ÿ
⁄
*cascade08⁄
€
 *cascade08€
›
*cascade08›
ﬂ
 *cascade08ﬂ
‡
*cascade08‡
·
 *cascade08·
„
*cascade08„
‰
 *cascade08‰
™*cascade08™´ *cascade08´±*cascade08±≤ *cascade08≤∫*cascade08∫ª *cascade08ªæ*cascade08æø *cascade08ø¡*cascade08¡¬ *cascade08¬…*cascade08…  *cascade08 Ã*cascade08ÃŒ *cascade08Œ”*cascade08”‘ *cascade08‘◊*cascade08◊Ÿ *cascade08Ÿ·*cascade08·‚ *cascade08‚„*cascade08„‰ *cascade08‰Î*cascade08Îë *cascade08ë§*cascade08§√ *cascade08√…*cascade08…å *cascade08åç*cascade08çö *cascade08ö‰*cascade08‰Ò *cascade08ÒÙ*cascade08Ùˆ *cascade08ˆ˙*cascade08˙Ñ *cascade08ÑÖ*cascade08ÖÜ *cascade08Üá*cascade08áä *cascade08äã*cascade08ã∫ *cascade08∫¿*cascade08¿Ú *cascade08Úç*cascade08ç™ *cascade08™π*cascade08π∫ *cascade08∫ª*cascade08ªΩ *cascade08Ωæ*cascade08æø *cascade08ø¿*cascade08¿¬ *cascade08¬√*cascade08√Ò *cascade08ÒÛ*cascade08Ûë *cascade08ëí*cascade08íø *cascade08ø¿*cascade08¿… *cascade08…–*cascade08–È *cascade08ÈÍ*cascade08ÍÌ *cascade08ÌÓ*cascade08ÓÅ *cascade08ÅÇ*cascade08Ç“ *cascade08“◊*cascade08◊¸ *cascade08¸í*cascade08íï *cascade08ï†*cascade08†≈ *cascade08≈÷*cascade08÷à *cascade08à†*cascade08†° *cascade08°®*cascade08®© *cascade08©Æ*cascade08ÆØ *cascade08Øπ*cascade08πÀ *cascade08À–*cascade08–‰ *cascade08‰Â*cascade08ÂÈ *cascade08ÈÍ*cascade08Í¢ *cascade08¢£*cascade08£Ã *cascade08ÃÉ*cascade08Éª *cascade08ª”*cascade08”‘ *cascade08‘‰*cascade08‰Ê *cascade08ÊÏ*cascade08Ï˛ *cascade08˛É*cascade08Éó *cascade08óò*cascade08òú *cascade08úù*cascade08ù’ *cascade08’÷*cascade08÷ˇ *cascade08ˇ∂*cascade08∂Ê *cascade08Ê˛*cascade08˛ˇ *cascade08ˇÜ*cascade08Üá *cascade08áå*cascade08åç *cascade08çó*cascade08ó© *cascade08©Æ*cascade08Æ¬ *cascade08¬ƒ*cascade08ƒ« *cascade08«…*cascade08…Å *cascade08ÅÇ*cascade08ÇÏ *cascade08Ï«*cascade08«¯ *cascade08¯ê*cascade08êë *cascade08ë†*cascade08†¢ *cascade08¢©*cascade08©ª *cascade08ª¿*cascade08¿‘ *cascade08‘÷*cascade08÷Ÿ *cascade08Ÿ€*cascade08€ì *cascade08ìî*cascade08î˛ *cascade08˛Ÿ*cascade08Ÿä *cascade08äé*cascade08éè *cascade08èë*cascade08ë£ *cascade08£®*cascade08®º *cascade08ºæ*cascade08æ¡ *cascade08¡√*cascade08√Ÿ *cascade08ŸÁ*cascade08ÁÛ *cascade08Ûü *cascade08ü ∞  *cascade08∞ æ *cascade08æ …  *cascade08… À *cascade08À Ã  *cascade08Ã ˙ *cascade08˙ ¢! *cascade08¢!∂!*cascade08∂!æ! *cascade08æ!∆!*cascade08∆!«! *cascade08«!Ã!*cascade08Ã!Õ! *cascade08Õ!–!*cascade08–!—! *cascade08—!◊!*cascade08◊!Ô! *cascade08Ô!Ù!*cascade08Ù!ı! *cascade08ı!ˆ!*cascade08ˆ!˜! *cascade08˜!¯!*cascade08¯!˘! *cascade08˘!˛!*cascade08˛!ˇ! *cascade08ˇ!Å"*cascade08Å"Ç" *cascade08Ç"Ö"*cascade08Ö"á" *cascade08á"ç"*cascade08ç"ê" *cascade08ê"ë"*cascade08ë"ì" *cascade08ì"î"*cascade08î"ï" *cascade08ï"ü"*cascade08ü"ß" *cascade08ß"è#*cascade08è#ß# *cascade08ß#º#*cascade08º#Â# *cascade08Â#˚#*cascade08˚#¸# *cascade08¸#ç$*cascade08ç$é$ *cascade08é$ï$*cascade08ï$ñ$ *cascade08ñ$ù$*cascade08ù$û$ *cascade08û$∆$*cascade08∆$«$ *cascade08«$$*cascade08$Ú$ *cascade08Ú$¥%*cascade08¥%µ% *cascade08µ%∏%*cascade08∏%π% *cascade08π%√'*cascade08√'ƒ' *cascade08ƒ'«'*cascade08«'…' *cascade08…'Õ'*cascade08Õ'Œ' *cascade08Œ'”'*cascade08”'’' *cascade08’'⁄'*cascade08⁄'€' *cascade08€'ﬁ'*cascade08ﬁ'ﬂ' *cascade08ﬂ'·'*cascade08·'Â' *cascade08Â'À(*cascade08À(›( *cascade08›(„(*cascade08„(Ú( *cascade08Ú(Ü)*cascade08Ü)á) *cascade08á)‹)*cascade08‹)›) *cascade08›)‚)*cascade08‚)„) *cascade08„)‰)*cascade08‰)Ê) *cascade08Ê)Á)*cascade08Á)Î) *cascade08Î)ü**cascade08ü*†* *cascade08†*•**cascade08•*®* *cascade08®*™**cascade08™*¨* *cascade08¨*…**cascade08…*ˇe *cascade08ˇeëf*cascade08ëfíf *cascade08ífñf*cascade08ñfóf *cascade08óföf*cascade08öfúf *cascade08úf°f*cascade08°f®f *cascade08®f¨f*cascade08¨f≠f *cascade08≠f≥f*cascade08≥f¥f *cascade08¥f∂f*cascade08∂f∏f *cascade08∏fπf*cascade08πf∫f *cascade08∫fªf*cascade08ªfºf *cascade08ºfæf*cascade08æføf *cascade08øfƒf*cascade08ƒf∆f *cascade08∆f f*cascade08 fÃf *cascade08Ãf”f*cascade08”fÇg *cascade082"file:///c:/Users/Tomi/FOREX/app.py