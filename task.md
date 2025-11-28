# Twelve Data API Integration

## Goal
Replace yfinance with Twelve Data API for accurate forex pricing that matches XTB broker feeds.

## Tasks

### [/] Phase 1: Setup & Configuration
- [x] Research Twelve Data batch request API
- [x] Plan rate limit strategy (15 sec refresh = 4 calls/min, well under 8/min limit)
- [ ] User registers for Twelve Data free account
- [ ] User generates API key
- [ ] Add API key to Streamlit secrets

### [ ] Phase 2: Core Implementation  
- [ ] Create `twelve_data_connector.py` module
  - [ ] Batch request function for 3 pairs
  - [ ] Error handling & fallback
  - [ ] Response parsing
- [ ] Update `requirements.txt` (requests already included)
- [ ] Modify `app.py` to use Twelve Data
  - [ ] Replace `get_data()` function
  - [ ] Update symbol naming (GBPUSD=X → GBP/USD)
  - [ ] Add API status indicator to sidebar

### [ ] Phase 3: Testing & Verification
- [ ] Test batch request locally
- [ ] Compare Twelve Data prices vs XTB
- [ ] Test London Box calculation accuracy
- [ ] Deploy to Streamlit Cloud
- [ ] Verify 24h uptime without hitting rate limits

### [ ] Phase 4: Documentation
- [ ] Update README with Twelve Data setup
- [ ] Document API key configuration
- [ ] Add troubleshooting guide
