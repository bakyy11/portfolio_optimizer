# --- NASTAVENIA PORTFÓLIA ---

# Zoznam tickerov z Yahoo Finance (tvoj mix z predošlých testov)
TICKERS = ['SPY', 'BTC-USD', 'QQQ', '^STOXX50E', 'EGLN.L']

# Počiatočný dátum pre sťahovanie dát
START_DATE = "2000-01-01"

# --- MATEMATICKÉ KONŠTANTY ---

# Ročná bezriziková miera (napr. 2% = 0.02)
# Používa sa pre výpočet Sharpe a Sortino Ratio
RISK_FREE_RATE = 0.02

# Predvolený seed pre numpy, aby boli výsledky reprodukovateľné (ako na image_40d0ab.png)
DEFAULT_SEED = 42

# 1. Nastav si svoju hranicu bolesti (napr. -15%)
MAX_ALLOWED_DRAWDOWN = -0.40

# --- CESTY K SÚBOROM ---

# Priečinok, kam sa budú ukladať tvoje vizualizácie (podľa vzoru image_40df73.png)
OUTPUT_DIR = "results"