import yfinance as yf
import pandas as pd
from .settings import START_DATE

def get_data(tickers):
    """Stiahne dáta z Yahoo Finance a vráti denné výnosy."""
    try:
        data = yf.download(tickers, start=START_DATE)['Close']
        # Odstránenie riadkov s chýbajúcimi dátami (napr. pred rokom 2014 pre BTC)
        data = data.dropna()
        
        if data.empty:
            return None
            
        returns = data.pct_change().dropna()
        return returns
    except Exception as e:
        print(f"Chyba pri sťahovaní dát: {e}")
        return None