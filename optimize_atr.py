import pandas as pd
import os
import itertools
import time
from src.strategy import TightenedSuperTrend

def optimize():
    start_time = time.time()
    symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT']
    data_dir = 'data'
    data = {}

    # Load Data
    for symbol in symbols:
        file_path = os.path.join(data_dir, f'{symbol}.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, index_col='timestamp', parse_dates=True)
            data[symbol] = df

    if not data:
        print("No data loaded. Exiting.")
        return

    # Optimization ranges
    sl_multipliers = [1.5, 2.0, 2.5]
    tp_multipliers = [2.5, 3.0, 3.5, 4.0]
    
    combinations = list(itertools.product(sl_multipliers, tp_multipliers))
    results = []

    print(f"Running optimization for {len(combinations)} combinations...")

    # Pre-process signals once
    base_strategy = TightenedSuperTrend(symbols=symbols)
    processed_data = {}
    for symbol, df in data.items():
        processed_data[symbol] = base_strategy.generate_signals(df)

    for sl, tp in combinations:
        # Instantiate Strategy with new multipliers
        strategy = TightenedSuperTrend(
            symbols=symbols, 
            adx_threshold=30.0,
            garch_sl_mult=sl,
            garch_tp_mult=tp
        )

        # Run Backtest
        backtest_results = strategy.run_backtest(processed_data)
        trades = backtest_results.get('trades', [])
        
        if not trades:
            results.append({
                'SL': sl, 'TP': tp, 'Total Trades': 0, 'Win Rate': 0, 
                'Net PnL': 0, 'Profit Factor': 0, 'Sharpe Ratio': 0, 'Max Drawdown': 0
            })
            continue

        trades_df = pd.DataFrame([vars(t) for t in trades])
        
        num_trades = len(trades_df)
        win_rate = (trades_df['win'].mean()) * 100
        net_pnl = trades_df['pnl'].sum()
        
        # Calculate stats
        gross_profit = trades_df[trades_df['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else float('inf')
        
        # Simple Sharpe (assuming 0 risk-free rate)
        sharpe = trades_df['pnl'].mean() / trades_df['pnl'].std() if trades_df['pnl'].std() != 0 else 0
        
        # Max Drawdown estimation (simplified)
        equity = 10000 + trades_df['pnl'].cumsum()
        peak = equity.cummax()
        drawdown = (equity - peak) / peak
        max_drawdown = drawdown.min() * 100

        results.append({
            'SL': sl,
            'TP': tp,
            'Total Trades': num_trades,
            'Win Rate': round(win_rate, 2),
            'Net PnL': round(net_pnl, 2),
            'Profit Factor': round(profit_factor, 2),
            'Sharpe Ratio': round(sharpe, 2),
            'Max Drawdown': round(max_drawdown, 2)
        })

    # Display results
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(by='Net PnL', ascending=False)
    
    print("\nOptimization Results:")
    print(results_df.to_string(index=False))
    print(f"\nTotal runtime: {time.time() - start_time:.2f} seconds")

if __name__ == '__main__':
    optimize()
