import argparse 
import sys 
from .project import get_data 
from .settings import TICKERS, RISK_FREE_RATE, DEFAULT_SEED, MAX_ALLOWED_DRAWDOWN
from .simulation import run_simulation

def main():
    # 1. Nastavenie argumentov terminálu 
    parser = argparse.ArgumentParser(description="Monte Carlo Portfolio Optimizer")
    
    parser.add_argument("-n", "--num_sim", type=int, default=20000, 
                        help="Počet simulovaných portfólií (default: 20000)")
    parser.add_argument("-s", "--seed", type=int, default=DEFAULT_SEED, 
                        help=f"Seed pre náhodné čísla (default: {DEFAULT_SEED})")
    parser.add_argument("-p", "--plot", action="store_true", 
                        help="Zobraziť vizualizácie po skončení simulácie")
    
    args = parser.parse_args()

    print(f"--- Štartujem optimalizáciu pre: {', '.join(TICKERS)} ---")

    # 2. Získanie dát (cez project.py)
    returns = get_data(TICKERS)
    if returns is None:
        print("Chyba: Nepodarilo sa stiahnuť dáta.")
        sys.exit(1)

    # 3. Spustenie simulácie (cez simulation.py)
    print(f"Spúšťam {args.num_sim} simulácií so seedom {args.seed}...")
    best_portfolio, df_results = run_simulation(returns, args.num_sim, args.seed, RISK_FREE_RATE)

    # 4. Výpis najlepších výsledkov (inšpirované tvojimi predošlými výstupmi)
    print("\n" + "="*30)
    print("NAJLEPŠIA ALOKÁCIA (SORTINO)")
    print("="*30)
    for ticker, weight in best_portfolio['weights'].items():
        print(f"{ticker:10}: {weight:.2%}")
    
    print("-" * 30)
    print(f"Očakávaný výnos: {best_portfolio['return']:.2%}")
    print(f"Downside Risk:   {best_portfolio['downside_risk']:.2%}")
    print(f"Sortino Ratio:   {best_portfolio['sortino']:.2f}")
    print(f"Max Drawdown:    {best_portfolio['max_drawdown']:.2%}")
    print(f"Sharpe Ratio:    {best_portfolio['sharpe']:.2f}")
    print(f"Calmar Ratio:    {best_portfolio['calmar']:.2f}")
    print("="*30)

    # 5. Volanie grafov (ak je zadaný prepínač --plot)
    if args.plot:
        from .simulation import save_results
        save_results(df_results, best_portfolio, returns)

if __name__ == "__main__":
    main()
