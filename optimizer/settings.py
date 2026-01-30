# --- SETTINGS OF PORTFOLIO ---

# List of tickers from Yahoo Finance 
TICKERS = ['SPY', 'QQQ', 'TLT', 'GLD', 'GSG', 'BTC-USD']

# Start date for data retrieval (YYYY-MM-DD)
START_DATE = "2000-01-01"

# Based on what choose best portfolio
METRIC = 'Sortino'  # Options: 'Return', 'Sortino', 'Sharpe', 'Calmar', 'MaxDD', 'TotalRisk', 'DownsideRisk'

# Function to check portfolio constraints
def check_constraints(weights, tickers):
    w = dict(zip(tickers, weights))
    
    # Stocks 40%, max 60%
    equity_sum = w.get('SPY', 0) + w.get('QQQ', 0)
    if equity_sum < 0.40 or equity_sum > 0.60: return False

    # Gold
    if w.get('GLD', 0) > 0.15: return False
    
    # Bonds at least 15%, hedge
    if w.get('TLT', 0) < 0.15: return False

    # Bitcoin fix 5% (allowed spread 6-8%)
    if not (0.06 <= w.get('BTC-USD', 0) <= 0.08): return False

    # Commodities at least 5%
    if w.get('GSG', 0) < 0.05: return False

    return True

    

# --- MATHEMATICS CONSTANTS ---

# Annual risk free rate (eg. 2% = 0.02)
# To calculate Sharpe a Sortino Ratio
RISK_FREE_RATE = 0.02

# SEED for random number generator
DEFAULT_SEED = 42

# Set your maximum allowed drawdown (eg. -40% = -0.40)
MAX_ALLOWED_DRAWDOWN = -0.25

# --- FILES ---

# Folder to save results
OUTPUT_DIR = "results"