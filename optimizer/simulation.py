import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from .settings import MAX_ALLOWED_DRAWDOWN

# def check_constraints(weights, tickers):
#     w = dict(zip(tickers, weights))
    
#     # PRAVIDLO 1: Bitcoin (Max 5%)
#     if w.get('BTC-USD', 0) > 0.05:
#         return False
        
#     # 1. MOTOR: SPY + QQQ musí tvoriť aspoň polovicu portfólia
#     if (w.get('SPY', 0) + w.get('QQQ', 0)) < 0.50:
#         return False

#     # 2. LIMIT TECH: QQQ môže ísť až na 30% (predtým 20%)
#     if w.get('QQQ', 0) > 0.30:
#         return False
        
#     if (w.get('GLD', 0) + w.get('TLT', 0)) < 0.25:
#         return False
        
#     return True

def run_simulation(returns, num_sim, seed, risk_free_rate):
    np.random.seed(seed)
    tickers = returns.columns
    risk_free_daily = risk_free_rate / 252

    results = []
    weights_record = []

    for i in range(num_sim):
        # 1. Náhodné váhy
        weights = np.random.random(len(tickers))
        weights /= np.sum(weights)

        # if not check_constraints(weights, tickers):
        #     continue  # Ak nespĺňa limity, tento pokus zahodíme a ideme na ďalší

        weights_record.append(weights)

        # 2. Výnosy portfólia
        p_returns = returns.dot(weights)
        ann_return = p_returns.mean() * 252

        # 3. Sortino Ratio (Downside Risk)
        downside_returns = p_returns[p_returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252)
        sortino = (ann_return - risk_free_rate) / downside_std if downside_std != 0 else 0

        # 4. Sharpe Ratio (Total Risk)
        total_std = p_returns.std() * np.sqrt(252)
        sharpe = (ann_return - risk_free_rate) / total_std

        # 5. Max Drawdown & Calmar
        cumulative = (1 + p_returns).cumprod()
        running_max = cumulative.cummax()
        drawdown_series = (cumulative - running_max) / running_max
        max_dd = drawdown_series.min()
        calmar = ann_return / abs(max_dd) if max_dd != 0 else 0

        results.append([ann_return, downside_std, total_std, sortino, sharpe, max_dd, calmar])

    # Analýza výsledkov
    columns = ['Return', 'DownsideRisk', 'TotalRisk', 'Sortino', 'Sharpe', 'MaxDD', 'Calmar']
    df = pd.DataFrame(results, columns=columns)


    # 2. Vyfiltruj len portfóliá, ktoré spĺňajú podmienku
    filtered_df = df[df['MaxDD'] >= MAX_ALLOWED_DRAWDOWN]

    # 3. Vyber najlepšie z nich (podľa Sortina alebo Výnosu)
    if not filtered_df.empty:
        # Ak existujú portfóliá pod 15% drawdown, zober to s najlepším Sortinom
        best_idx = filtered_df['Sortino'].idxmax()
        print(f"Nájdené portfólio spĺňajúce limit Drawdown {MAX_ALLOWED_DRAWDOWN:.0%}")
    else:
        # Ak si v 100k simuláciách nenašiel nič také bezpečné, zober aspoň to najmenej rizikové
        best_idx = df['MaxDD'].idxmax()
        print(f"VAROVANIE: Žiadne portfólio nespĺňa limit {MAX_ALLOWED_DRAWDOWN:.0%}. Vyberám najbezpečnejšie možné.")
    
    # Príprava balíčka s najlepším portfóliom
    best_portfolio = {
        'weights': dict(zip(tickers, weights_record[best_idx])),
        'return': df.loc[best_idx, 'Return'],
        'downside_risk': df.loc[best_idx, 'DownsideRisk'],
        'sortino': df.loc[best_idx, 'Sortino'],
        'max_drawdown': df.loc[best_idx, 'MaxDD'],
        'sharpe': df.loc[best_idx, 'Sharpe'],
        'calmar': df.loc[best_idx, 'Calmar'],
        'idx': best_idx
    }

    return best_portfolio, df

def save_results(df, best_portfolio, returns):
    """Vytvorí samostatný priečinok pre tento run a uloží grafy aj report."""
    from .settings import OUTPUT_DIR
    import os
    
    # 1. Príprava priečinkov
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_folder = f"{OUTPUT_DIR}/run_{timestamp}"
    
    if not os.path.exists(run_folder):
        os.makedirs(run_folder)

    # 2. Uloženie TEXTOVÉHO REPORTU
    report_path = f"{run_folder}/report.txt"
    with open(report_path, "w") as f:
        f.write("=== MONTE CARLO OPTIMIZATION REPORT ===\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write("-" * 40 + "\n")
        f.write("NAJLEPŠIA ALOKÁCIA:\n")
        for ticker, weight in best_portfolio['weights'].items():
            f.write(f"{ticker:12}: {weight:.2%}\n")
        f.write("-" * 40 + "\n")
        f.write(f"Očakávaný výnos: {best_portfolio['return']:.2%}\n")
        f.write(f"Max Drawdown:    {best_portfolio['max_drawdown']:.2%}\n")
        f.write(f"Sortino Ratio:   {best_portfolio['sortino']:.2f}\n")
        f.write(f"Downside Risk:   {best_portfolio['downside_risk']:.2%}\n")
        f.write("-" * 40 + "\n")
        # 1. Zoznam tickerov (aby si vedel, čo si v ten deň testoval)
        f.write(f"TESTOVANÉ AKTÍVA: {', '.join(returns.columns.tolist())}\n")
        
        # 2. Výpočet a zápis priemernej korelácie (dôkaz diverzifikácie)
        avg_corr = returns.corr().values[np.triu_indices_from(returns.corr(), k=1)].mean()
        f.write(f"PRIEMERNÁ KORELÁCIA: {avg_corr:.2f}\n")
        f.write("="*40 + "\n")

    # 3. GRAF: Efficient Frontier
    plt.figure(figsize=(10, 6))
    plt.scatter(df['TotalRisk'], df['Return'], c=df['Sortino'], cmap='viridis', s=10, alpha=0.3)
    plt.colorbar(label='Sortino Ratio')
    plt.scatter(best_portfolio['downside_risk'], best_portfolio['return'], color='red', marker='*', s=200)
    plt.title(f'Efficient Frontier (Run: {timestamp})')
    plt.savefig(f"{run_folder}/efficient_frontier.png")
    plt.close()

    # 4. GRAF: Equity & Drawdown
    best_weights = np.array(list(best_portfolio['weights'].values()))
    p_returns = returns.dot(best_weights)
    cumulative = (1 + p_returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    ax1.plot(cumulative.index, cumulative, color='green')
    ax1.set_title(f'Equity Curve - Return: {best_portfolio["return"]:.2%}')
    ax2.fill_between(drawdown.index, drawdown, 0, color='red', alpha=0.3)
    ax2.set_title(f'Underwater Chart - MaxDD: {best_portfolio["max_drawdown"]:.2%}')
    
    plt.savefig(f"{run_folder}/performance_summary.png")
    plt.close()
    
    print(f"✅ Všetky dáta a grafy boli uložené do: {run_folder}")