import pandas as pd
import numpy as np
import glob
import json
import os

def run_monte_carlo():
    # 1. Read all trades
    trade_files = glob.glob("*_trades.csv")
    all_trades = []
    for f in trade_files:
        df = pd.read_csv(f)
        all_trades.append(df)
    
    trades = pd.concat(all_trades, ignore_index=True)
    pnls = trades['pnl'].dropna().to_numpy()

    # 2. Monte Carlo setup
    num_simulations = 10000
    num_trades = len(pnls)
    initial_capital = 10000
    
    equity_curves = np.zeros((num_simulations, num_trades + 1))
    equity_curves[:, 0] = initial_capital
    
    # 3. Simulation
    for i in range(num_simulations):
        # Bootstrap resampling
        resampled_pnls = np.random.choice(pnls, size=num_trades, replace=True)
        equity = initial_capital
        for j in range(num_trades):
            equity += resampled_pnls[j]
            equity_curves[i, j+1] = equity
            
    # 4. Statistics
    final_equities = equity_curves[:, -1]
    
    summary = {
        "Mean Final Equity": float(np.mean(final_equities)),
        "Median Final Equity": float(np.median(final_equities)),
        "Best Case": float(np.max(final_equities)),
        "Worst Case": float(np.min(final_equities)),
        "5th Percentile": float(np.percentile(final_equities, 5)),
        "95th Percentile": float(np.percentile(final_equities, 95)),
        "Probability of Loss": float(np.mean(final_equities < initial_capital))
    }
    
    # 5. Output
    print(json.dumps(summary, indent=4))
    
    # 6. Save results
    pd.DataFrame(equity_curves).to_csv("monte_carlo_results.csv", index=False)
    with open("monte_carlo_summary.json", "w") as f:
        json.dump(summary, f, indent=4)

if __name__ == "__main__":
    run_monte_carlo()
