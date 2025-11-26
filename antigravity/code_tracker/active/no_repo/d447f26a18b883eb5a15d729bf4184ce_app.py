¾}import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import timedelta

# Page config
st.set_page_config(page_title="Forex MintaillesztÅ‘", layout="wide")

def download_data(ticker, interval="1d"):
    """Downloads historical data for the given ticker."""
    try:
        period = "max"
        if interval == "1h":
            period = "2y"
        elif interval == "15m":
            period = "60d"

        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df.empty:
            return None
        
        # Ensure we have a flat index if MultiIndex is returned
        if isinstance(df.columns, pd.MultiIndex):
            # Try to get the specific ticker level
            if ticker in df.columns.get_level_values(1):
                df = df.xs(ticker, axis=1, level=1)
            # If that fails or structure is different, check if we have 'Close' at top level or just one column
            elif 'Close' in df.columns.get_level_values(0):
                 # This might happen if yfinance returns MultiIndex with (Price, Ticker)
                 pass 

        # Flatten columns if they are MultiIndex but we just want to access 'Close' easily
        # A robust way for single ticker download:
        if isinstance(df.columns, pd.MultiIndex):
             # If we have (Price, Ticker), just taking 'Close' might return a Series or DataFrame depending on structure
             try:
                 df = df['Close']
             except KeyError:
                 # Fallback: if columns are just tickers, or something else
                 pass

        # If df is a Series (just Close prices), convert to DataFrame
        if isinstance(df, pd.Series):
            df = df.to_frame(name='Close')
        
        # If we still don't have 'Close' but have data, assume single column is Close
        if 'Close' not in df.columns and df.shape[1] == 1:
            df.columns = ['Close']

        # Final check
        if 'Close' in df.columns:
            # Ensure we have OHLC for candlestick
            required_cols = ['Open', 'High', 'Low', 'Close']
            # If we are missing some, we can't do candlestick properly, but let's try to return what we have
            # or just return Close if others are missing (fallback to line chart? No, user asked for candlestick)
            # yfinance usually returns all.
            available_cols = [c for c in required_cols if c in df.columns]
            if len(available_cols) == 4:
                return df[available_cols].dropna()
            elif 'Close' in df.columns:
                 # Fallback if something is wrong, but try to keep structure
                 return df[['Close']].dropna()
        
        return None
    except Exception as e:
        st.error(f"Hiba az adatok letÃ¶ltÃ©sekor: {e}")
        return None

def normalize(series):
    """Normalizes a series to start at 0 (percentage change)."""
    if len(series) == 0:
        return series
    return (series / series.iloc[0]) - 1

def find_top_patterns(data, window_size=30, prediction_horizon=30, top_n=5):
    """
    Finds the top N most similar historical patterns based on correlation.
    Returns a list of (index, correlation) tuples and the total count of high-correlation matches (>0.8).
    """
    if len(data) < window_size * 2 + prediction_horizon:
        return [], 0

    # Target pattern: the last `window_size` days
    target = data['Close'].iloc[-window_size:]
    target_norm = normalize(target).values
    target_std = np.std(target_norm)

    matches = []
    high_corr_count = 0

    # Iterate through history
    search_limit = len(data) - window_size - prediction_horizon - 1 
    close_prices = data['Close'].values
    
    for i in range(search_limit):
        window = close_prices[i : i + window_size]
        
        # Normalize window
        if window[0] == 0: continue
        window_norm = (window / window[0]) - 1
        window_std = np.std(window_norm)
        
        # Correlation
        if window_std > 1e-9 and target_std > 1e-9:
            corr = np.corrcoef(target_norm, window_norm)[0, 1]
            
            if corr > 0.80:
                high_corr_count += 1
            
            matches.append((i, corr))

    # Sort by correlation descending
    matches.sort(key=lambda x: x[1], reverse=True)
    
    # Select top N non-overlapping
    top_matches = []
    indices = set()
    
    for idx, corr in matches:
        if len(top_matches) >= top_n:
            break
        
        # Check overlap (ensure new match is at least window_size/2 away from existing ones)
        is_overlapping = False
        for existing_idx in indices:
            if abs(idx - existing_idx) < window_size // 2:
                is_overlapping = True
                break
        
        if not is_overlapping:
            top_matches.append((idx, corr))
            indices.add(idx)

    return top_matches, high_corr_count

def main():
    st.title("ğŸ“ˆ Forex MintaillesztÅ‘ Motor")
    st.markdown("""
    Ez az alkalmazÃ¡s megkeresi a leghasonlÃ³bb mÃºltbeli Ã¡rfolyammozgÃ¡st az elmÃºlt idÅ‘szakhoz kÃ©pest, 
    Ã©s kivetÃ­ti a jÃ¶vÅ‘beli lehetsÃ©ges mozgÃ¡st a mÃºltbeli minta alapjÃ¡n.
    """)

    # Sidebar
    st.sidebar.header("BeÃ¡llÃ­tÃ¡sok")
    
    # Forex Only Symbols
    forex_symbols = [
        'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDHUF=X', 
        'EURHUF=X', 'AUDUSD=X', 'USDCAD=X', 'USDCHF=X'
    ]
    ticker = st.sidebar.selectbox("VÃ¡lassz EszkÃ¶zt", forex_symbols)
    
    interval = st.sidebar.selectbox("IdÅ‘sÃ­k", ["1d", "1h", "15m"])
    st.sidebar.info("""â„¹ï¸ AdatkorlÃ¡tok:
- Napos: Teljes elÅ‘zmÃ©ny
- Ã“rÃ¡s: Max 2 Ã©v
- 15 perces: Max 60 nap""")

    window_size = st.sidebar.slider("Minta hossza (gyertya)", min_value=10, max_value=90, value=30)
    prediction_horizon = st.sidebar.slider("ElÅ‘rejelzÃ©s hossza (gyertya)", min_value=5, max_value=60, value=30)

    if st.sidebar.button("ElemzÃ©s futtatÃ¡sa"):
        with st.spinner("Adatok letÃ¶ltÃ©se Ã©s elemzÃ©se..."):
            data = download_data(ticker, interval)
            
            if data is not None and not data.empty:
                st.success(f"Adatok sikeresen letÃ¶ltve: {len(data)} gyertya")
                
                # Find top patterns
                top_matches, match_count = find_top_patterns(data, window_size, prediction_horizon)
                
                if top_matches:
                    # Prepare data for plotting
                    current_data = data.iloc[-window_size:]
                    last_price = current_data['Close'].iloc[-1]
                    last_date = current_data.index[-1]
                    
                    # Metrics
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("EszkÃ¶z", ticker)
                    col1.metric("DÃ¡tum", str(last_date.date()))
                    
                    best_match_idx = top_matches[0][0]
                    best_match_date = data.index[best_match_idx]
                    col2.metric("Legjobb talÃ¡lat", str(best_match_date.date()))
                    
                    # Confidence Index Logic
                    confidence_label = "Alacsony"
                    delta_color = "normal"
                    
                    if match_count > 10:
                        confidence_label = "Magas"
                        delta_color = "normal" # Green
                    elif match_count < 3:
                        confidence_label = "-Alacsony" # Red
                        delta_color = "normal"
                    else:
                        confidence_label = "KÃ¶zepes"
                        delta_color = "off" # Gray

                    col4.metric("Bizalmi Index", f"{match_count} db hasonlÃ³", confidence_label, delta_color=delta_color)

                    # Visualization
                    fig = go.Figure()

                    # 1. Current Price (Candlestick)
                    # Check if we have OHLC data
                    if 'Open' in data.columns and 'High' in data.columns and 'Low' in data.columns:
                        fig.add_trace(go.Candlestick(
                            x=data.index,
                            open=data['Open'],
                            high=data['High'],
                            low=data['Low'],
                            close=data['Close'],
                            name='Jelenlegi Ãrfolyam',
                            increasing_line_color='green', 
                            decreasing_line_color='red'
                        ))
                    else:
                        # Fallback to line if OHLC missing
                        fig.add_trace(go.Scatter(
                            x=data.index, 
                            y=data['Close'], 
                            mode='lines', 
                            name='Jelenlegi Ãrfolyam',
                            line=dict(color='blue', width=2)
                        ))

                    # Generate dates for projection
                    # Ensure seamless connection: Start from last_date (index 0)
                    if interval in ['1h', '15m']:
                        step = timedelta(hours=1) if interval == '1h' else timedelta(minutes=15)
                        projection_dates = [last_date + (step * i) for i in range(prediction_horizon + 1)]
                    else:
                        projection_dates = [last_date + timedelta(days=i) for i in range(prediction_horizon + 1)]

                    # 2. Ghost Cloud (Top 5 Matches)
                    projection_paths = []
                    
                    for idx, corr in top_matches:
                        # Get historical projection
                        hist_proj = data['Close'].iloc[idx + window_size : idx + window_size + prediction_horizon]
                        
                        # Calculate returns
                        proj_returns = hist_proj.pct_change().fillna(0)
                        
                        # Reconstruct price path
                        # Start with last_price to connect seamlessly
                        path = [last_price]
                        for ret in proj_returns.iloc[0:]: # Use all returns to build path of length prediction_horizon + 1
                            path.append(path[-1] * (1 + ret))
                        
                        hist_proj_values = data['Close'].iloc[idx + window_size : idx + window_size + prediction_horizon + 1].values
                        
                        if len(hist_proj_values) > 0:
                            start_price = data['Close'].iloc[idx + window_size - 1] 
                            hist_seq = data['Close'].iloc[idx + window_size - 1 : idx + window_size + prediction_horizon].values
                            
                            if len(hist_seq) > 1:
                                norm_seq = hist_seq / hist_seq[0] # Starts at 1.0
                                path = last_price * norm_seq
                                
                                # Ensure path matches dates length
                                if len(path) < len(projection_dates):
                                    path = np.pad(path, (0, len(projection_dates) - len(path)), 'constant', constant_values=np.nan)
                                elif len(path) > len(projection_dates):
                                    path = path[:len(projection_dates)]
                                
                                projection_paths.append(path)

                                # Plot Ghost Line
                                fig.add_trace(go.Scatter(
                                    x=projection_dates, 
                                    y=path, 
                                    mode='lines', 
                                    name=f'MÃºltbeli: {data.index[idx].date()} (Corr: {corr:.2f})',
                                    line=dict(color='grey', width=1),
                                    opacity=0.3,
                                    showlegend=False 
                                ))

                    # Add one legend item for the ghosts
                    fig.add_trace(go.Scatter(
                        x=[None], y=[None],
                        mode='lines',
                        name='MÃºltbeli hasonlÃ³k (Top 5)',
                        line=dict(color='grey', width=1),
                        opacity=0.3
                    ))

                    # 3. Average Projection
                    if projection_paths:
                        # Filter out paths with NaNs for mean calculation if any
                        valid_paths = [p for p in projection_paths if not np.isnan(p).any()]
                        if valid_paths:
                            avg_path = np.mean(valid_paths, axis=0)
                            fig.add_trace(go.Scatter(
                                x=projection_dates, 
                                y=avg_path, 
                                mode='lines', 
                                name='Ãtlagos vÃ¡rhatÃ³ Ãºt',
                                line=dict(color='orange', width=3, dash='dash'),
                                showlegend=True
                            ))

                    # Calculate initial view range (last ~60 candles + projection)
                    initial_range_candles = 60 # Changed from 100 to 60 for bigger candles
                    if len(data) > initial_range_candles:
                        start_view = data.index[-initial_range_candles]
                    else:
                        start_view = data.index[0]
                    
                    end_view = projection_dates[-1]

                    fig.update_layout(
                        title=f"{ticker} ElemzÃ©s Ã©s ProjekciÃ³ (Ghost Cloud)",
                        xaxis_title="IdÅ‘",
                        yaxis_title="Ãr",
                        template="plotly_white",
                        hovermode="x unified",
                        dragmode='pan',
                        legend=dict(
                            yanchor="top",
                            y=0.99,
                            xanchor="left",
                            x=0.01
                        ),
                        xaxis=dict(
                            tickformat="%H:%M\n%d %b",
                            range=[start_view, end_view],
                            rangebreaks=[dict(bounds=["sat", "mon"])], # Hide weekends
                            showspikes=True,
                            spikemode='across',
                            rangeslider=dict(visible=False) # Ensure disabled in layout dict too
                        ),
                        yaxis=dict(
                            autorange=True,
                            fixedrange=False,
                            tickformat='.5f',
                            showspikes=True,
                            spikemode='across'
                        )
                    )
                    
                    # Explicitly disable rangeslider to prevent Y-axis locking
                    fig.update_xaxes(rangeslider_visible=False)

                    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

                else:
                    st.warning("Nincs elÃ©g adat a mintaillesztÃ©shez.")
            else:
                st.error("Nem sikerÃ¼lt adatokat letÃ¶lteni. EllenÅ‘rizd a szimbÃ³lumot!")

if __name__ == "__main__":
    main()
Ë *cascade08ËË*cascade08ËŒ *cascade08Œ›*cascade08›ä *cascade08äô*cascade08ôœ *cascade08œ³*cascade08³´ *cascade08´µ*cascade08µ÷ *cascade08÷*cascade08 *cascade08ó*cascade08ó– *cascade08–›*cascade08›œ *cascade08œ°*cascade08°± *cascade08±¶*cascade08¶· *cascade08·¸*cascade08¸¹ *cascade08¹Á*cascade08ÁÂ *cascade08ÂÒ*cascade08ÒÔ *cascade08ÔÙ*cascade08ÙÚ *cascade08Úö*cascade08öø *cascade08ø¢*cascade08¢Á *cascade08ÁÂ*cascade08ÂÃ *cascade08ÃÒ*cascade08ÒÓ *cascade08ÓÜ*cascade08Üİ *cascade08İè*cascade08èé *cascade08éê*cascade08êë *cascade08ë†	*cascade08†	‡	 *cascade08‡		*cascade08	¬	 *cascade08¬	Â	*cascade08Â	Å	 *cascade08Å	Æ	*cascade08Æ	Ç	 *cascade08Ç	Î	*cascade08Î	Ï	 *cascade08Ï	â	*cascade08â	ã	 *cascade08ã	ë	*cascade08ë	ì	 *cascade08ì	ÿ	*cascade08ÿ	
 *cascade08
…
*cascade08…
†
 *cascade08†
‘
*cascade08‘
’
 *cascade08’
–
*cascade08–
—
 *cascade08—
¢
*cascade08¢
£
 *cascade08£
¥
*cascade08¥
¦
 *cascade08¦
§
*cascade08§
¨
 *cascade08¨
¯
*cascade08¯
°
 *cascade08°
¶
*cascade08¶
¸
 *cascade08¸
¹
*cascade08¹
º
 *cascade08º
¾
*cascade08¾
À
 *cascade08À
Ò
*cascade08Ò
Ô
 *cascade08Ô
á
*cascade08á
â
 *cascade08â
÷
*cascade08÷
ø
 *cascade08ø
™*cascade08™š *cascade08šœ*cascade08œ *cascade08¦*cascade08¦° *cascade08°³*cascade08³´ *cascade08´µ*cascade08µº *cascade08º»*cascade08»¼ *cascade08¼½*cascade08½¾ *cascade08¾È*cascade08ÈÊ *cascade08ÊÖ*cascade08Ö× *cascade08×å*cascade08åæ *cascade08æô*cascade08ôƒ *cascade08ƒœ*cascade08œ *cascade08£*cascade08£ª *cascade08ª­*cascade08­® *cascade08®Ú*cascade08ÚÛ *cascade08Ûê*cascade08êë *cascade08ëì*cascade08ìó *cascade08ó—*cascade08—® *cascade08®¹*cascade08¹½ *cascade08½Ò*cascade08ÒÓ *cascade08Óß*cascade08ßà *cascade08àâ*cascade08âã *cascade08ã‚*cascade08‚ƒ *cascade08ƒ†*cascade08†ˆ *cascade08ˆ*cascade08 *cascade08*cascade08¬ *cascade08¬»*cascade08»¼ *cascade08¼Ä*cascade08ÄÅ *cascade08Åµ*cascade08µ¸ *cascade08¸Ö*cascade08Öõ *cascade08õÿ*cascade08ÿ€ *cascade08€*cascade08‚ *cascade08‚*cascade08‘ *cascade08‘¼*cascade08¼Æ *cascade08Æ× *cascade08×Û*cascade08ÛÜ *cascade08Üì*cascade08ìí *cascade08í›*cascade08›œ *cascade08œ *cascade08 ¡ *cascade08¡Î*cascade08ÎÏ *cascade08Ïú*cascade08úû *cascade08ûÿ*cascade08ÿ€ *cascade08€™*cascade08™› *cascade08›î*cascade08îù *cascade08ùú *cascade08ú€*cascade08€ *cascade08„*cascade08„ *cascade08—*cascade08—™ *cascade08™¡*cascade08¡« *cascade08«±*cascade08±² *cascade08²µ*cascade08µ¶ *cascade08¶¿*cascade08¿Á *cascade08ÁÂ*cascade08ÂÃ *cascade08ÃÊ*cascade08ÊÌ *cascade08Ìö*cascade08ö÷ *cascade08÷§*cascade08§¨ *cascade08¨­*cascade08­® *cascade08®Ä*cascade08ÄÅ *cascade08ÅĞ*cascade08ĞÒ *cascade08ÒÖ*cascade08Ö× *cascade08×æ*cascade08æç *cascade08çè*cascade08èé *cascade08é‚*cascade08‚ƒ *cascade08ƒÎ*cascade08ÎÏ *cascade08ÏÜ*cascade08Üİ *cascade08İŞ*cascade08Şà *cascade08àä *cascade08äè*cascade08èï *cascade08ïğ*cascade08ğû *cascade08ûü *cascade08üˆ*cascade08ˆ‰ *cascade08‰œ *cascade08œ¥*cascade08¥À *cascade08ÀÆ*cascade08ÆÊ *cascade08ÊÎ *cascade08ÎŞ*cascade08Şß *cascade08ßå *cascade08åæ*cascade08æç *cascade08çí*cascade08íî *cascade08îï*cascade08ïğ *cascade08ğô*cascade08ôõ *cascade08õö *cascade08öø *cascade08øù *cascade08ùú *cascade08úû*cascade08ûŠ *cascade08Š*cascade08 *cascade08“*cascade08“” *cascade08”•*cascade08•š *cascade08š›*cascade08›œ *cascade08œ*cascade08 *cascade08 *cascade08 ¡ *cascade08¡¢*cascade08¢¤ *cascade08¤¥*cascade08¥¦ *cascade08¦¨*cascade08¨ª *cascade08ª­*cascade08­± *cascade08±³*cascade08³¸ *cascade08¸¹ *cascade08¹º*cascade08º» *cascade08»½*cascade08½Ç *cascade08ÇÈ*cascade08ÈÉ *cascade08ÉÑ*cascade08ÑÓ *cascade08Ó×*cascade08×Ø *cascade08ØÙ*cascade08ÙÛ *cascade08Ûİ*cascade08İß *cascade08ßæ*cascade08æç *cascade08çí *cascade08íò*cascade08òú *cascade08ú‰*cascade08‰Š *cascade08ŠŒ*cascade08Œ *cascade08*cascade08 *cascade08”*cascade08”• *cascade08•›*cascade08›œ *cascade08œ¨*cascade08¨© *cascade08©¬*cascade08¬­ *cascade08­» *cascade08»½*cascade08½ç *cascade08çè *cascade08è‘*cascade08‘’ *cascade08’•*cascade08•– *cascade08–œ*cascade08œ *cascade08Í*cascade08ÍÏ *cascade08Ï× *cascade08×İ*cascade08İŞ *cascade08Şß *cascade08ßà *cascade08àá*cascade08áä *cascade08äì*cascade08ìí *cascade08íğ*cascade08ğñ *cascade08ñò*cascade08òó *cascade08óö*cascade08ö÷ *cascade08÷ù*cascade08ùÿ *cascade08ÿ„*cascade08„† *cascade08†‡ *cascade08‡ˆ*cascade08ˆ‰ *cascade08‰‹*cascade08‹ *cascade08‘ *cascade08‘’ *cascade08’š*cascade08š  *cascade08 ¡ *cascade08¡¢*cascade08¢£ *cascade08£±*cascade08±² *cascade08²´*cascade08´µ *cascade08µ¶*cascade08¶· *cascade08·º*cascade08º» *cascade08»Ã*cascade08ÃÄ *cascade08ÄÅ *cascade08Å¤ *cascade08¤­ *cascade08­ *cascade08› *cascade08›©*cascade08©ª *cascade08ª¯*cascade08¯° *cascade08°×*cascade08×Ø *cascade08ØÚ*cascade08ÚÛ *cascade08ÛÜ *cascade08Ü–  *cascade08– — *cascade08— ˜  *cascade08˜ š  *cascade08š  *cascade08 §  *cascade08§ © *cascade08© Ê  *cascade08Ê Ì  *cascade08Ì Î! *cascade08Î!Ü!*cascade08Ü!‰" *cascade08‰"¹"*cascade08¹"¾" *cascade08¾"ä"*cascade08ä"æ" *cascade08æ"«#*cascade08«#¬# *cascade08¬#É#*cascade08É#Ê# *cascade08Ê#Ş#*cascade08Ş#ß# *cascade08ß#é#*cascade08é#ì# *cascade08ì#î#*cascade08î#ğ# *cascade08ğ#ƒ$*cascade08ƒ$‰$ *cascade08‰$‘$*cascade08‘$’$ *cascade08’$¶$*cascade08¶$·$ *cascade08·$¹$*cascade08¹$º$ *cascade08º$Š%*cascade08Š%Œ% *cascade08Œ%%*cascade08%% *cascade08%‘%*cascade08‘%’% *cascade08’%¢&*cascade08¢&£& *cascade08£&«&*cascade08«&¬& *cascade08¬&®&*cascade08®&¯& *cascade08¯&°& *cascade08°&³&*cascade08³&·& *cascade08·&Ù'*cascade08Ù'Û' *cascade08Û'ï'*cascade08ï'ó' *cascade08ó'õ'*cascade08õ'ö' *cascade08ö'‰(*cascade08‰(Š( *cascade08Š((*cascade08(( *cascade08(’(*cascade08’(—( *cascade08—(¤(*cascade08¤(§( *cascade08§(¨( *cascade08¨(²(*cascade08²(³( *cascade08³(´(*cascade08´(¶( *cascade08¶(™)*cascade08™)š) *cascade08š))*cascade08) ) *cascade08 )ª)*cascade08ª)«) *cascade08«)Ç)*cascade08Ç)È) *cascade08È)Ñ)*cascade08Ñ)Ò) *cascade08Ò)è)*cascade08è)é) *cascade08é)ï)*cascade08ï)ğ) *cascade08ğ)›**cascade08›*œ* *cascade08œ*¨**cascade08¨*©* *cascade08©*¯**cascade08¯*°* *cascade08°*±**cascade08±*²* *cascade08²*Ş**cascade08Ş*à* *cascade08à*å**cascade08å*æ* *cascade08æ*è**cascade08è*é* *cascade08é*î**cascade08î*ï* *cascade08ï*ı**cascade08ı*ş* *cascade08ş*‚+*cascade08‚+ˆ+ *cascade08ˆ+“+*cascade08“+•+ *cascade08•+º,*cascade08º,», *cascade08»,¼,*cascade08¼,½, *cascade08½,Â,*cascade08Â,Ã, *cascade08Ã,ß,*cascade08ß,á, *cascade08á,ï,*cascade08ï,ğ, *cascade08ğ,ˆ-*cascade08ˆ-‰- *cascade08‰-‘-*cascade08‘-’- *cascade08’-”-*cascade08”-•- *cascade08•-¢-*cascade08¢-£- *cascade08£-×-*cascade08×-Ø- *cascade08Ø-ä-*cascade08ä-å- *cascade08å-ç-*cascade08ç-è- *cascade08è-ƒ.*cascade08ƒ.†. *cascade08†.™.*cascade08™.š. *cascade08š.¤.*cascade08¤.¦. *cascade08¦.§.*cascade08§.¨. *cascade08¨.ª.*cascade08ª.«. *cascade08«.².*cascade08².³. *cascade08³.¶.*cascade08¶.·. *cascade08·.¹.*cascade08¹.º. *cascade08º.Å.*cascade08Å.È. *cascade08È.×.*cascade08×.Ú. *cascade08Ú.İ.*cascade08İ.Ş. *cascade08Ş.à.*cascade08à.á. *cascade08á.ç.*cascade08ç.è. *cascade08è.ñ.*cascade08ñ.ò. *cascade08ò.û.*cascade08û.ü. *cascade08ü.€/*cascade08€// *cascade08/„/*cascade08„/…/ *cascade08…/Ê/*cascade08Ê/Ì/ *cascade08Ì/ã/*cascade08ã/ä/ *cascade08ä/é/*cascade08é/ê/ *cascade08ê/½0*cascade08½0¾0 *cascade08¾0Á0*cascade08Á0Â0 *cascade08Â0Æ0*cascade08Æ0Ç0 *cascade08Ç0ë0*cascade08ë0ü0 *cascade08ü0¶1*cascade08¶1·1 *cascade08·1ì1*cascade08ì1í1 *cascade08í1±2*cascade08±2²2 *cascade08²2À2*cascade08À2Ã2 *cascade08Ã2Ä2*cascade08Ä2Å2 *cascade08Å2Ì2*cascade08Ì2Í2 *cascade08Í2Õ2*cascade08Õ2á2 *cascade08á2‚3 *cascade08‚3†3*cascade08†3‹3 *cascade08‹3Œ3 *cascade08Œ33 *cascade0833*cascade083 3 *cascade08 3¡3 *cascade08¡3£3*cascade08£3¤3 *cascade08¤3ª3*cascade08ª3µ3 *cascade08µ3¶3 *cascade08¶3À3 *cascade08À3Ä3*cascade08Ä3É3 *cascade08É3Ë3 *cascade08Ë3Ì3*cascade08Ì3œ4 *cascade08œ4 4*cascade08 4¡4 *cascade08¡4£4*cascade08£4¤4 *cascade08¤4¥4*cascade08¥4¦4*cascade08¦4¨4 *cascade08¨4×4*cascade08×4Ù4 *cascade08Ù4ª5 *cascade08ª5«5*cascade08«5®5 *cascade08®5°5*cascade08°5±5 *cascade08±5³5*cascade08³5·5 *cascade08·5¿5*cascade08¿5Ã5 *cascade08Ã5Ì5*cascade08Ì5Î5 *cascade08Î5Ñ5*cascade08Ñ5Ò5 *cascade08Ò5Ô5*cascade08Ô5ë5 *cascade08ë5ì5*cascade08ì5í5 *cascade08í5î5*cascade08î5÷5 *cascade08÷5ÿ5*cascade08ÿ5Š6 *cascade08Š6Œ6*cascade08Œ6¾6 *cascade08¾6¿6 *cascade08¿6ø6*cascade08ø6ù6 *cascade08ù6–7*cascade08–7—7 *cascade08—77*cascade0877 *cascade087§7*cascade08§7¨7 *cascade08¨7¯7*cascade08¯7°7 *cascade08°7Ó7*cascade08Ó7Ô7 *cascade08Ô7Ş7*cascade08Ş7ß7 *cascade08ß7â7 *cascade08â7å7*cascade08å7Š8 *cascade08Š8¡8*cascade08¡8¢8 *cascade08¢8£8*cascade08£8¤8 *cascade08¤8«8*cascade08«8¬8 *cascade08¬8°8*cascade08°8²8 *cascade08²8¶8*cascade08¶8¸8 *cascade08¸8Ï8*cascade08Ï8Ğ8 *cascade08Ğ8Ú8*cascade08Ú8Û8 *cascade08Û8Ü8 *cascade08Ü8İ8*cascade08İ8ã8 *cascade08ã8ä8*cascade08ä8æ8 *cascade08æ8ê8*cascade08ê8í8 *cascade08í8î8*cascade08î8ï8 *cascade08ï8ñ8*cascade08ñ8ò8 *cascade08ò8û8*cascade08û8ı8 *cascade08ı8„9*cascade08„99 *cascade0899*cascade089§9 *cascade08§9«9*cascade08«9¬9 *cascade08¬9±9*cascade08±9µ9 *cascade08µ9·9*cascade08·9º9 *cascade08º9À9*cascade08À9Â9 *cascade08Â9Í9*cascade08Í9Î9 *cascade08Î9Õ9*cascade08Õ9Ö9 *cascade08Ö9Ø9 *cascade08Ø9İ9*cascade08İ9ã9 *cascade08ã9î9*cascade08î9ü9 *cascade08ü9‚:*cascade08‚:„: *cascade08„:ä:*cascade08ä:å: *cascade08å:;*cascade08;; *cascade08;ª;*cascade08ª;«; *cascade08«;ß;*cascade08ß;à; *cascade08à;á;*cascade08á;â; *cascade08â;ã;*cascade08ã;ä; *cascade08ä;Š<*cascade08Š<‹< *cascade08‹<¢<*cascade08¢<£< *cascade08£<¥<*cascade08¥<¯< *cascade08¯<°< *cascade08°<Ã<*cascade08Ã<Å< *cascade08Å<ö<*cascade08ö<÷< *cascade08÷<…=*cascade08…=†= *cascade08†=‹= *cascade08‹=Œ=*cascade08Œ=Æ= *cascade08Æ=Ç= *cascade08Ç=ö=*cascade08ö=÷= *cascade08÷=´>*cascade08´>µ> *cascade08µ>¹>*cascade08¹>º> *cascade08º>á>*cascade08á>â> *cascade08â>Å? *cascade08Å?»@ *cascade08»@¿@*cascade08¿@À@ *cascade08À@£A*cascade08£A¤A *cascade08¤A¨A*cascade08¨A©A *cascade08©A®A*cascade08®A¯A*cascade08¯A°A *cascade08°AÂA*cascade08ÂAÃA *cascade08ÃAÓA*cascade08ÓAÔA *cascade08ÔA×A*cascade08×AØA *cascade08ØAB*cascade08B‚B *cascade08‚B•B*cascade08•B«B *cascade08«B¬B *cascade08¬B½B*cascade08½B¾B *cascade08¾BÎB*cascade08ÎBÏB *cascade08ÏBßB*cascade08ßBàB*cascade08àBäB*cascade08äBåB *cascade08åBˆC*cascade08ˆC‰C *cascade08‰C•C*cascade08•C–C *cascade08–CœC*cascade08œCC *cascade08C½C*cascade08½C¾C *cascade08¾C¿C *cascade08¿CÂC*cascade08ÂCÄC*cascade08ÄCÅC *cascade08ÅCÆC*cascade08ÆCÙC*cascade08ÙCÚC *cascade08ÚCïC*cascade08ïCğC *cascade08ğCúC*cascade08úCûC *cascade08ûCıC *cascade08ıC‹D*cascade08‹DŒD *cascade08ŒDŸD*cascade08ŸD D*cascade08 D¨D*cascade08¨D©D *cascade08©D­D*cascade08­D®D *cascade08®DµD*cascade08µD¶D *cascade08¶D¸D *cascade08¸D¯E*cascade08¯EíE *cascade08íEîE *cascade08îE†F*cascade08†F‡F*cascade08‡F‰F *cascade08‰FŠF*cascade08ŠF¢F*cascade08¢F¤F *cascade08¤F¨F*cascade08¨FïF *cascade08ïFóF*cascade08óFƒG *cascade08ƒG„G*cascade08„GœG *cascade08œGŸG*cascade08ŸGÊG *cascade08ÊGÎG*cascade08ÎGŞG *cascade08ŞGáG*cascade08áGùG *cascade08ùGúG*cascade08úG—H *cascade08—H›H*cascade08›HÑH *cascade08ÑHÒH*cascade08ÒHÕH *cascade08ÕHÙH*cascade08ÙH‰I *cascade08‰I—I*cascade08—I˜I *cascade08˜II*cascade08I¼I *cascade08¼IJ*cascade08JJ*cascade08JJ *cascade08J‘J*cascade08‘J’J *cascade08’J“J*cascade08“J–J *cascade08–J«J*cascade08«JÅJ *cascade08ÅJÆJ*cascade08ÆJÈJ *cascade08ÈJÉJ*cascade08ÉJÊJ *cascade08ÊJËJ*cascade08ËJÌJ *cascade08ÌJÜJ *cascade08ÜJİJ*cascade08İJŞJ *cascade08ŞJßJ *cascade08ßJáJ*cascade08áJâJ *cascade08âJêJ *cascade08êJëJ*cascade08ëJíJ *cascade08íJîJ*cascade08îJòJ *cascade08òJóJ *cascade08óJ÷J*cascade08÷JøJ *cascade08øJŒK *cascade08ŒKÍK*cascade08ÍKÎK *cascade08ÎKÏK*cascade08ÏKÑK *cascade08ÑKÒK *cascade08ÒKÕK*cascade08ÕKÖK *cascade08ÖK×K*cascade08×KØK *cascade08ØKÚK*cascade08ÚKÛK *cascade08ÛKáK *cascade08áKäK *cascade08äKæK*cascade08æKèK *cascade08èKëK*cascade08ëKìK *cascade08ìKîK*cascade08îKğK *cascade08ğKõK*cascade08õKöK *cascade08öKùK*cascade08ùK’L *cascade08’L”L*cascade08”L®L *cascade08®L¯L*cascade08¯L´L *cascade08´LµL*cascade08µL¶L *cascade08¶LÀL*cascade08ÀLÁL *cascade08ÁLÂL*cascade08ÂLÃL *cascade08ÃLÅL*cascade08ÅLÆL *cascade08ÆLÍL*cascade08ÍLÎL *cascade08ÎLÔL*cascade08ÔLÕL *cascade08ÕLÖL*cascade08ÖL×L *cascade08×LïL *cascade08ïLğL *cascade08ğL€M*cascade08€MM *cascade08M…M*cascade08…M†M *cascade08†M‰M*cascade08‰MŸM *cascade08ŸM M*cascade08 M¡M *cascade08¡M£M*cascade08£M¤M *cascade08¤M©M*cascade08©MªM *cascade08ªM«M*cascade08«M¬M *cascade08¬M®M*cascade08®M¯M *cascade08¯M°M*cascade08°M±M *cascade08±M²M*cascade08²M³M *cascade08³M´M*cascade08´MµM *cascade08µM¶M*cascade08¶M·M *cascade08·M¸M*cascade08¸M¹M *cascade08¹M»M*cascade08»M¼M *cascade08¼M½M*cascade08½MÕM *cascade08ÕMêM*cascade08êM—N *cascade08—NšN*cascade08šNœN *cascade08œN§N*cascade08§N¨N *cascade08¨NªN*cascade08ªN«N *cascade08«N¬N*cascade08¬N®N *cascade08®N³N*cascade08³NÍN *cascade08ÍNÑN*cascade08ÑNÒN *cascade08ÒNÔN*cascade08ÔNÕN *cascade08ÕNÖN*cascade08ÖN×N *cascade08×NÙN*cascade08ÙNÛN *cascade08ÛNÜN*cascade08ÜNŞN *cascade08ŞNßN*cascade08ßNäN *cascade08äNåN*cascade08åNæN *cascade08æNèN*cascade08èN‚O *cascade08‚OO*cascade08OO *cascade08O£O*cascade08£O¤O *cascade08¤O¨O*cascade08¨O©O *cascade08©O®O*cascade08®O¯O *cascade08¯OÁO*cascade08ÁOÂO *cascade08ÂOÃO*cascade08ÃOÄO *cascade08ÄOÅO*cascade08ÅOÆO *cascade08ÆOÌO*cascade08ÌOÍO *cascade08ÍOÜO*cascade08ÜOP *cascade08P—P*cascade08—P›P *cascade08›P£P *cascade08£P£P*cascade08£P½P *cascade08½P¾P*cascade08¾PÀP *cascade08ÀPÃP*cascade08ÃPÄP *cascade08ÄPÅP*cascade08ÅPÆP *cascade08ÆPÇP*cascade08ÇPÈP *cascade08ÈPÍP*cascade08ÍPÎP *cascade08ÎPãP*cascade08ãPåP *cascade08åPìP*cascade08ìP‚Q *cascade08‚Q†Q*cascade08†QˆQ *cascade08ˆQŒQ*cascade08ŒQ Q *cascade08 Q§Q*cascade08§Q©Q *cascade08©Q®Q*cascade08®Q¯Q *cascade08¯Q±Q*cascade08±Q²Q *cascade08²Q·Q*cascade08·Q¸Q *cascade08¸QÒQ *cascade08ÒQ™R*cascade08™RšR *cascade08šRœR *cascade08œRŸR*cascade08ŸR R *cascade08 R£R*cascade08£R¤R *cascade08¤R¥R*cascade08¥R¦R *cascade08¦R©R*cascade08©RªR *cascade08ªRÇR*cascade08ÇRÈR *cascade08ÈRÌR*cascade08ÌRÍR *cascade08ÍRÎR*cascade08ÎRĞR *cascade08ĞR×R*cascade08×RØR *cascade08ØRÚR*cascade08ÚRÛR *cascade08ÛRŞR*cascade08ŞRßR *cascade08ßRãR *cascade08ãRäR*cascade08äRçR *cascade08çR¨S*cascade08¨SĞS *cascade08ĞSÑS *cascade08ÑSÔS*cascade08ÔSÖS *cascade08ÖSâS*cascade08âSäS *cascade08äSæS*cascade08æSéS *cascade08éST*cascade08TƒT *cascade08ƒT„T*cascade08„T˜T *cascade08˜T›T*cascade08›T«T *cascade08«T­T *cascade08­T‚V *cascade08‚V„V *cascade08„V‹V*cascade08‹VŒV *cascade08ŒVV*cascade08VV *cascade08VŸV*cascade08ŸV V *cascade08 V®V *cascade08®VûW *cascade08ûWüW *cascade08üW€X*cascade08€XX *cascade08XÕY*cascade08ÕYÙY *cascade08ÙYÚY *cascade08ÚYßY*cascade08ßYòY*cascade08òYóY *cascade08óYöY*cascade08öY÷Y *cascade08÷YøY*cascade08øYúY *cascade08úY­Z *cascade08­Z²Z *cascade08²Z³Z *cascade08³ZµZ*cascade08µZ¶Z *cascade08¶Z¸Z*cascade08¸ZåZ *cascade08åZæZ *cascade08æZéZ *cascade08éZîZ*cascade08îZïZ *cascade08ïZğZ*cascade08ğZñZ *cascade08ñZóZ*cascade08óZôZ *cascade08ôZ[*cascade08[‚[ *cascade08‚[…[*cascade08…[†[ *cascade08†[Š[*cascade08Š[‹[ *cascade08‹[Œ[*cascade08Œ[[ *cascade08[˜[*cascade08˜[™[ *cascade08™[[*cascade08[[ *cascade08[Ä[*cascade08Ä[Æ[ *cascade08Æ[Î[*cascade08Î[Ò[*cascade08Ò[æ[ *cascade08æ[\*cascade08\£\ *cascade08£\§\*cascade08§\Û]*cascade08Û]İ] *cascade08İ]Ş]*cascade08Ş]á] *cascade08á]ã]*cascade08ã]å] *cascade08å]ç]*cascade08ç]è] *cascade08è]é]*cascade08é]ë] *cascade08ë]ì]*cascade08ì]î] *cascade08î]ó]*cascade08ó]‡^ *cascade08‡^‰^*cascade08‰^‹^ *cascade08‹^^*cascade08^—^*cascade08—^™^ *cascade08™^š^*cascade08š^œ^ *cascade08œ^ ^*cascade08 ^¡^ *cascade08¡^¥^*cascade08¥^¦^ *cascade08¦^©^ *cascade08©^±^*cascade08±^Ğ^ *cascade08Ğ^Ñ^ *cascade08Ñ^Ó^*cascade08Ó^Ô^ *cascade08Ô^Ø^*cascade08Ø^İ^ *cascade08İ^ÿ^ *cascade08ÿ^‡_*cascade08‡_Š_ *cascade08Š_‹_ *cascade08‹_‘_ *cascade08‘_’_*cascade08’_®_ *cascade08®_µ_*cascade08µ_º_ *cascade08º_¼_ *cascade08¼_¿_*cascade08¿_Á_ *cascade08Á_Ã_*cascade08Ã_Å_ *cascade08Å_Í_*cascade08Í_á_ *cascade08á_ø_*cascade08ø_ù_ *cascade08ù_ş_*cascade08ş_ÿ_ *cascade08ÿ_‚`*cascade08‚`ƒ` *cascade08ƒ`–`*cascade08–`˜` *cascade08˜`š`*cascade08š`›` *cascade08›``*cascade08`Ÿ` *cascade08Ÿ`ª` *cascade08ª`¬`*cascade08¬`È` *cascade08È`Î`*cascade08Î`Ğ` *cascade08Ğ`Ñ`*cascade08Ñ`Ò` *cascade08Ò`Ô`*cascade08Ô`Õ` *cascade08Õ`Ö`*cascade08Ö`×` *cascade08×`Û`*cascade08Û`İ` *cascade08İ`ç`*cascade08ç`è` *cascade08è`a *cascade08a•a*cascade08•a–a *cascade08–a˜a *cascade08˜aša*cascade08ša›a *cascade08›a£a *cascade08£a¦a*cascade08¦aÂa *cascade08ÂaÇa*cascade08ÇaÎa *cascade08ÎaĞa *cascade08ĞaÔa*cascade08Ôa×a *cascade08×aØa *cascade08ØaÚa*cascade08ÚaÛa *cascade08Ûaàa*cascade08àaûa *cascade08ûaşa *cascade08şa€b*cascade08€b”b *cascade08”b¸b*cascade08¸bƒc *cascade08ƒc†c*cascade08†cˆc *cascade08ˆcc*cascade08cc *cascade08c‘c*cascade08‘c’c *cascade08’c“c*cascade08“c®c *cascade08®c²c*cascade08²c³c *cascade08³c¶c*cascade08¶c·c *cascade08·cºc*cascade08ºcÛc *cascade08ÛcŞc*cascade08Şcßc *cascade08ßcác*cascade08ácåc *cascade08åcéc*cascade08écêc *cascade08êcöc*cascade08öc£d *cascade08£d¥d*cascade08¥d¦d *cascade08¦d§d*cascade08§d¨d *cascade08¨d±d*cascade08±d²d *cascade08²dØd*cascade08Ødğd *cascade08ğdòd*cascade08òdˆe *cascade08ˆeŸe*cascade08Ÿeµe *cascade08µe¶e*cascade08¶e·e *cascade08·e¿e*cascade08¿eÀe *cascade08Àeãe *cascade08ãeñe*cascade08ñeòe *cascade08òeµf*cascade08µf¶f *cascade08¶fºf*cascade08ºf»f *cascade08»f¿f *cascade08¿fÀf*cascade08ÀfÃf *cascade08ÃfÄf*cascade08ÄfÅf *cascade08ÅfÍf*cascade08ÍfÎf *cascade08ÎfÏf*cascade08ÏfÔf *cascade08ÔfÕf *cascade08Õf×f*cascade08×fØf *cascade08ØfÚf*cascade08ÚfÛf *cascade08Ûfßf *cascade08ßfŞg*cascade08Şgég *cascade08égíg*cascade08ígˆh *cascade08ˆh h *cascade08 h¤h*cascade08¤h¼h *cascade08¼hÀh*cascade08ÀhÂh *cascade08ÂhÃh*cascade08ÃhÄh *cascade08ÄhÆh*cascade08ÆhÇh *cascade08ÇhÉh*cascade08ÉhÊh *cascade08ÊhËh*cascade08ËhÌh *cascade08ÌhÍh*cascade08ÍhÎh *cascade08ÎhĞh*cascade08ĞhÑh *cascade08ÑhÒh*cascade08Òhîh *cascade08îhòh*cascade08òhöh*cascade08öhøh *cascade08øhÿh*cascade08ÿh€i *cascade08€i„i *cascade08„iˆi*cascade08ˆi«i *cascade08«i­i *cascade08­i°i*cascade08°i´i *cascade08´i¶i*cascade08¶iºi*cascade08ºiÒi *cascade08ÒiÔi*cascade08ÔiÚi *cascade08ÚiÜi*cascade08ÜiŞi *cascade08Şiâi*cascade08âiãi *cascade08ãiäi*cascade08äiçi *cascade08çièi*cascade08èiêi *cascade08êiïi*cascade08ïiñi *cascade08ñiòi*cascade08òiôi *cascade08ôiøi*cascade08øiüi*cascade08üi¥j *cascade08¥jªj*cascade08ªj«j *cascade08«j´j *cascade08´jµj*cascade08µjÁj *cascade08ÁjÃj *cascade08Ãjõj *cascade08õj÷j *cascade08÷jûj*cascade08ûjÿj*cascade08ÿj™k *cascade08™kÓk *cascade08ÓkÔk*cascade08Ôk™l *cascade08™l«l*cascade08«l®l *cascade08®lÇl*cascade08Çlén *cascade08én¯o *cascade08¯o°o*cascade08°o±o *cascade08±o²o*cascade08²o´o *cascade08´o»o*cascade08»o½o *cascade08½o¾o*cascade08¾oÃo *cascade08ÃoÏo*cascade08ÏoÑo *cascade08ÑoÖo*cascade08Öo×o *cascade08×oßo*cascade08ßoˆp *cascade08ˆpŒp*cascade08Œpµp *cascade08µp¸p*cascade08¸påp *cascade08åpêp*cascade08êpëp *cascade08ëpìp*cascade08ìpîp *cascade08îpîp*cascade08îp‚q *cascade08‚qq *cascade08qÇq *cascade08Çqs *cascade08s…t*cascade08…tÁt *cascade08Átˆu *cascade08ˆu‰u*cascade08‰u™u *cascade08™u÷u*cascade08÷uÚv*cascade08Úvöw *cascade08öw„y *cascade08„yy *cascade08yŸy *cascade08Ÿyµy *cascade08µyÜz*cascade08Üzßz *cascade08ßz¢{ *cascade08¢{¿{*cascade08¿{¾} *cascade082$file:///C:/Users/Tomi/.gemini/app.py