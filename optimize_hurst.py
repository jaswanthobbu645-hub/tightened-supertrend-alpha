import pandas as pd
import os
from src.strategy import TightenedSuperTrend

def run_optimization():
    symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT']
    data_dir = 'data'
    data = {}

    # Load Data
    for symbol in symbols:
        file_path = os.path.join(data_dir, f'{symbol}.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, index_col='timestamp', parse_dates=True)
            data[symbol] = df
        else:
            print(f"Warning: {file_path} not found.")

    if not data:
        print("No data loaded. Exiting.")
        return

    hurst_thresholds = [0.50, 0.52, 0.55, 0.58, 0.60]
    results_list = []

    print(f"{'Hurst':<10} | {'Trades':<8} | {'Win Rate':<10} | {'Net PnL':<12} | {'Profit Factor':<15} | {'Sharpe':<8} | {'Max DD %':<10}")
    print("-" * 90)

    for threshold in hurst_thresholds:
        # Instantiate Strategy with fixed ADX=30
        strategy = TightenedSuperTrend(symbols=symbols, adx_threshold=30.0)
        
        # Process data and run backtest
        processed_data = {}
        for symbol, df in data.items():
            df_signals = strategy.generate_signals(df, hurst_threshold=threshold)
            processed_data[symbol] = df_signals
        
        results = strategy.run_backtest(processed_data)
        
        # Extract results
        row = {
            'Hurst': threshold,
            'Total Trades': results['total_trades'],
            'Win Rate': f"{results['win_rate']:.2f}%",
            'Net PnL': f"${results['net_pnl']:.2f}",
            'Profit Factor': f"{results['profit_factor']:.2f}",
            'Sharpe Ratio': f"{results['sharpe_ratio']:.2f}",
            'Max Drawdown': f"{results['max_drawdown']:.2f}%"
        }
        
        print(f"{row['Hurst']:<10.2f} | {row['Total Trades']:<8} | {row['Win Rate']:<10} | {row['Net PnL']:<12} | {row['Profit Factor']:<15} | {row['Sharpe Ratio']:<8} | {row['Max Drawdown']:<10}")

if __name__ == '__main__':
    run_optimization()
