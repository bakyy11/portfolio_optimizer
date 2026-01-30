import argparse 
import sys 
from .project import get_data 
from .settings import TICKERS, RISK_FREE_RATE, DEFAULT_SEED, MAX_ALLOWED_DRAWDOWN, METRIC
from .simulation import run_simulation

def main():
    # 1. Setting up argument parser
    parser = argparse.ArgumentParser(description="Monte Carlo Portfolio Optimizer")
    
    parser.add_argument("-n", "--num_sim", type=int, default=20000, 
                        help="Amount of generated portfolios (default: 20000)")
    parser.add_argument("-s", "--seed", type=int, default=DEFAULT_SEED, 
                        help=f"Seed for random number generation (default: {DEFAULT_SEED})")
    parser.add_argument("-p", "--plot", action="store_true", 
                        help="Show visualizations after simulation is complete")
    
    args = parser.parse_args()

    print(f"--- Starting optimilization for: {', '.join(TICKERS)} ---")

    # 2. Retrieving data (via project.py)
    returns = get_data(TICKERS)
    if returns is None:
        print("Error: Could not retrieve data.")
        sys.exit(1)

    # 3. Starting simulation (via simulation.py)
    print(f"Generating {args.num_sim} simulations with seed {args.seed}...")
    best_portfolio, df_results = run_simulation(returns, args.num_sim, args.seed, RISK_FREE_RATE)

    # 4. Output 
    print("\n" + "="*30)
    print(f"BEST PORTFOLIO ({METRIC})")
    print("="*30)
    for ticker, weight in best_portfolio['weights'].items():
        print(f"{ticker:10}: {weight:.2%}")
    
    print("-" * 30)
    print(f"Expected Annual Return: {best_portfolio['return']:.2%}")
    print(f"Downside Risk:   {best_portfolio['downside_risk']:.2%}")
    print(f"Max Drawdown:    {best_portfolio['max_drawdown']:.2%}")
    print(f"Sortino Ratio:   {best_portfolio['sortino']:.2f}")
    print(f"Sharpe Ratio:    {best_portfolio['sharpe']:.2f}")
    print(f"Calmar Ratio:    {best_portfolio['calmar']:.2f}")
    print(f"Avg. Correlation {best_portfolio['avg_corr']:.2f}")
    print("="*30)

    # 5. Calling graphs (if is used --plot)
    if args.plot:
        from .simulation import save_results
        save_results(df_results, best_portfolio, returns)

if __name__ == "__main__":
    main()
