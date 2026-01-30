# Portfolio Optimizer (Monte Carlo Simulation)

A portfolio optimization tool designed to find the "Sweet Spot" between high returns and manageable risk. This tool uses Monte Carlo simulations to evaluate thousands of asset allocations and identifies the optimal portfolio based on the **Sortino Ratio** and **Max Drawdown** constraints.

## 🚀 Key Features
- **Monte Carlo Engine:** Simulates 100,000+ portfolio combinations.
- **Constraints:** Hard-coded safety limits (e.g., BTC max 5%, SPY min 15%) to ensure real-world viability.
- **Advanced Metrics:** Calculates Sharpe Ratio, Sortino Ratio, Calmar Ratio, and Max Drawdown.
- **Automated Reporting:** Generates timestamped folders with performance charts and text reports.
- **Risk Management:** Includes "Underwater Charts" to visualize historical drawdowns.

## 🛠 Project Structure
- `optimizer/` - Main package.
    - `settings.py` - User-defined parameters (tickers, dates, constraints).
    - `simulation.py` - Calculation engine and visualization logic.
    - `__main__.py` - Application entry point.
- `results/` - Automatically generated analysis reports (ignored by Git).
- `requirements.txt` - Required Python libraries.

## 📈 Sample Allocation (Optimized)
///

## 🔧 Installation & Usage
1. Clone the repo:
   ```bash
   git clone [https://github.com/bakyy11/portfolio-optimizer.git](https://github.com/bakyy11/portfolio-optimizer.git)