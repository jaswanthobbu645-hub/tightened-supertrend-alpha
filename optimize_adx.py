import pandas as pd
import os
from src.strategy import TightenedSuperTrend

def run_optimization():
    symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT']
    data_dir = 'data'
    data = {}

    for symbol in symbols:
        file_path = os.path.join(data_dir, f'{symbol}.csv')
        if os.path.exists(file_path):
            data[symbol] = pd.read_csv(file_path, index_col='timestamp', parse_dates=True)

    if not data:
        print("No data loaded.")
        return

    thresholds = [20, 22, 25, 28, 30, 35]
    results_list = []

    print(f"{'Threshold':<10} | {'Trades':<8} | {'WinRate':<8} | {'NetPnL':<12} | {'ProfFactor':<10} | {'Sharpe':<8} | {'MaxDD':<8}")
    print("-" * 80)

    for thresh in thresholds:
        strategy = TightenedSuperTrend(symbols=symbols, adx_threshold=float(thresh))
        
        processed_data = {}
        for symbol, df in data.items():
            processed_data[symbol] = strategy.generate_signals(df)
            
        stats = strategy.run_backtest(processed_data)
        
        results_list.append({
            'threshold': thresh,
            'trades': stats['total_trades'],
            'win_rate': stats['win_rate'],
            'pnl': stats['net_pnl'],
            'pf': stats['profit_factor'],
            'sharpe': stats['sharpe_ratio'],
            'mdd': stats['max_drawdown']
        })
        
        print(f"{thresh:<10} | {stats['total_trades']:<8} | {stats['win_rate']:<7.1f}% | ${stats['net_pnl']:<11.2f} | {stats['profit_factor']:<10.2f} | {stats['sharpe_ratio']:<8.2f} | {stats['max_drawdown']:<7.1f}%")

    # Select best (logic: net PnL * Profit Factor / MDD)
    best = max(results_list, key=lambda x: (x['pnl'] * x['pf']) / (x['mdd'] + 0.1))
    print("-" * 80)
    print(f"Recommended Threshold: {best['threshold']}")

if __name__ == '__main__':
    run_optimization()
