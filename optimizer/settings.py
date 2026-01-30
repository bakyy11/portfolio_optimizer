# --- SETTINGS OF PORTFOLIO ---

# List of tickers from Yahoo Finance 
TICKERS = ['SPY', 'BTC-USD', 'QQQ', '^STOXX50E', 'EGLN.L']

# Start date for data retrieval (YYYY-MM-DD)
START_DATE = "2000-01-01"

# Function to check portfolio constraints
def check_constraints(weights, tickers):
    w = dict(zip(tickers, weights))
    
    # RULE 1: Bitcoin (Max 5%)
    if w.get('BTC-USD', 0) > 0.05:
        return False
        
    # 1. ENGINE: SPY + QQQ at least 50%
    if (w.get('SPY', 0) + w.get('QQQ', 0)) < 0.50:
        return False

    # 2. LIMIT TECH: QQQ up to 30% 
    if w.get('QQQ', 0) > 0.30:
        return False
    # 3. STABILITY: GLD + TLT at least 25%    
    if (w.get('GLD', 0) + w.get('TLT', 0)) < 0.25:
        return False
        
    return True

    

# --- MATHEMATICS CONSTANTS ---

# Annual risk free rate (eg. 2% = 0.02)
# To calculate Sharpe a Sortino Ratio
RISK_FREE_RATE = 0.02

# SEED for random number generator
DEFAULT_SEED = 42

# Set your maximum allowed drawdown (eg. -40% = -0.40)
MAX_ALLOWED_DRAWDOWN = -0.40

# --- FILES ---

# Folder to save results
OUTPUT_DIR = "results"