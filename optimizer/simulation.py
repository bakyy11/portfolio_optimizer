import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from .settings import MAX_ALLOWED_DRAWDOWN, METRIC, check_constraints

def run_simulation(returns, num_sim, seed, risk_free_rate):
    np.random.seed(seed)
    tickers = returns.columns
    risk_free_daily = risk_free_rate / 252

    results = []
    weights_record = []

    for i in range(num_sim):
        # 1. Random weights
        weights = np.random.random(len(tickers))
        weights /= np.sum(weights)

        if not check_constraints(weights, tickers):
            continue # Skip portfolios that don't meet constraints

        weights_record.append(weights)

        # 2. Portfolio returns
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

        # 6. Correlation
        avg_corr = returns.corr().values[np.triu_indices_from(returns.corr(), k=1)].mean()

        results.append([ann_return, downside_std, total_std, sortino, sharpe, max_dd, calmar, avg_corr])

    # Analyze results
    columns = ['Return', 'DownsideRisk', 'TotalRisk', 'Sortino', 'Sharpe', 'MaxDD', 'Calmar', 'Correlation']
    df = pd.DataFrame(results, columns=columns)


    # 2. Filter portfolios by MAX_ALLOWED_DRAWDOWN
    filtered_df = df[df['MaxDD'] >= MAX_ALLOWED_DRAWDOWN]

    # 3. Choose the best portfolio
    if not filtered_df.empty:
        # If exists portfolios within the drawdown limit, pick the best Return
        best_idx = filtered_df[METRIC].idxmax()
        print(f"The best portfolio within drawdown limit {MAX_ALLOWED_DRAWDOWN:.0%}")
    else:
        # If none, pick the one with the least drawdown
        best_idx = df['MaxDD'].idxmax()
        print(f"WARNING: There is no portfolio within drawdown limit {MAX_ALLOWED_DRAWDOWN:.0%}. Choosing the safest portfolio.")
    
    # Prepare best portfolio details
    best_portfolio = {
        'weights': dict(zip(tickers, weights_record[best_idx])),
        'return': df.loc[best_idx, 'Return'],
        'downside_risk': df.loc[best_idx, 'DownsideRisk'],
        'sortino': df.loc[best_idx, 'Sortino'],
        'max_drawdown': df.loc[best_idx, 'MaxDD'],
        'sharpe': df.loc[best_idx, 'Sharpe'],
        'calmar': df.loc[best_idx, 'Calmar'],
        'avg_corr': df.loc[best_idx, 'Correlation'],
        'idx': best_idx
    }

    return best_portfolio, df

def save_results(df, best_portfolio, returns):
    from .settings import OUTPUT_DIR
    import os
    
    # 1. Preparing output folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_folder = f"{OUTPUT_DIR}/run_{timestamp}"
    
    if not os.path.exists(run_folder):
        os.makedirs(run_folder)

    # 2. Saving text report
    report_path = f"{run_folder}/report.txt"
    with open(report_path, "w") as f:
        f.write("=== MONTE CARLO OPTIMIZATION REPORT ===\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write("-" * 40 + "\n")
        f.write("THE BEST ALLOCATION:\n")
        for ticker, weight in best_portfolio['weights'].items():
            f.write(f"{ticker:12}: {weight:.2%}\n")
        f.write("-" * 40 + "\n")
        f.write(f"Expected Annual Return: {best_portfolio['return']:.2%}\n")
        f.write(f"Max Drawdown:    {best_portfolio['max_drawdown']:.2%}\n")
        f.write(f"Downside Risk:   {best_portfolio['downside_risk']:.2%}\n")
        f.write(f"Sortino Ratio:   {best_portfolio['sortino']:.2f}\n")
        f.write(f"Sharpe Ratio:    {best_portfolio['sharpe']:.2f}\n")
        f.write(f"Calmar Ratio:    {best_portfolio['calmar']:.2f}\n")
        f.write(f"Avg. Correlation {best_portfolio['avg_corr']:.2f}\n")
        f.write("-" * 40 + "\n")
        # 1. List of tested assets
        f.write(f"TESTED ASSETS: {', '.join(returns.columns.tolist())}\n")
        
        # 2. Average correlation
        f.write(f"AVERAGE CORRELATION: {best_portfolio['avg_corr']:.2f}\n")
        f.write("="*40 + "\n")

    # 3. GRAPH: Efficient Frontier
    plt.figure(figsize=(10, 6))
    plt.scatter(df['TotalRisk'], df['Return'], c=df['Sortino'], cmap='viridis', s=10, alpha=0.3)
    plt.colorbar(label='Sortino Ratio')
    plt.scatter(best_portfolio['downside_risk'], best_portfolio['return'], color='red', marker='.', s=200)
    plt.title(f'Efficient Frontier (Run: {timestamp})')
    plt.savefig(f"{run_folder}/efficient_frontier.png")
    plt.close()

    # 4. GRAPH: Equity & Drawdown
    best_weights = np.array(list(best_portfolio['weights'].values()))
    p_returns = returns.dot(best_weights)
    cumulative = (1 + p_returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    ax1.plot(cumulative.index, cumulative, color='#40eb34')
    ax1.set_title(f'Equity Curve - Return: {best_portfolio["return"]:.2%}')
    ax2.fill_between(drawdown.index, drawdown, 0, color='red', alpha=0.3)
    ax2.set_title(f'Underwater Chart - MaxDD: {best_portfolio["max_drawdown"]:.2%}')
    
    plt.savefig(f"{run_folder}/performance_summary.png")
    plt.close()
    
    print(f"✅ All data and graphs saved to: {run_folder}")