import pandas as pd
import os
import joblib
import json
import sys

# Add the directory to sys.path so we can import src.strategy
sys.path.append(os.getcwd())
from src.strategy import TightenedSuperTrend

def run_optimization():
    # Load files
    model = joblib.load('best_model.pkl')
    scaler = joblib.load('scaler.pkl') if os.path.exists('scaler.pkl') else None
    
    symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT']
    data_dir = 'data'
    data = {}
    
    for symbol in symbols:
        file_path = os.path.join(data_dir, f'{symbol}.csv')
        if os.path.exists(file_path):
            data[symbol] = pd.read_csv(file_path, index_col='timestamp', parse_dates=True)

    if not data:
        print("No data found in 'data/' directory.")
        return

    # Pre-generate base signals
    strategy = TightenedSuperTrend(symbols=symbols, adx_threshold=30.0)
    base_data = {}
    for symbol, df in data.items():
        df_signals = strategy.generate_signals(df)
        
        feature_cols_map = {
            'ema200_trend': (df_signals['close'] > df_signals['ema200']).astype(int),
            'ema50_trend': (df_signals['close'] > df_signals['ema50']).astype(int),
            'adx': df_signals['adx'],
            'hurst': df_signals['hurst'],
            'garch_vol': df_signals['garch_vol'],
            'atr_pct': df_signals['atr_pct'],
            'volume_ratio': (df_signals['volume'] / df_signals['vol_ma']).fillna(1),
            'st_fast_dir': df_signals['st_fast_dir'],
            'st_slow_dir': df_signals['st_slow_dir'],
            'rsi': df_signals['rsi'],
            'ema20_slope': df_signals['ema20_slope'],
            'ema50_slope': df_signals['ema50_slope'],
            'ema200_slope': df_signals['ema200_slope'],
            'macd_hist': df_signals['macd_hist'],
            'momentum20': df_signals['momentum20'],
            'momentum50': df_signals['momentum50']
        }

        feat_df = pd.DataFrame(feature_cols_map).fillna(0)
        if scaler:
            feat_df = scaler.transform(feat_df)
            
        df_signals['prob_win'] = model.predict_proba(feat_df)[:, 1]
        base_data[symbol] = df_signals

    thresholds = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75]
    results_list = []

    for t in thresholds:
        processed_data = {}
        for symbol, df in base_data.items():
            df_signals = df.copy()
            
            # Apply threshold
            mask = (df_signals['prob_win'] >= t)
            df_signals['long_signal'] = (df_signals['long_signal'] == True) & mask
            df_signals['short_signal'] = (df_signals['short_signal'] == True) & mask
            df_signals['long_size_factor'] = 1.0
            df_signals['short_size_factor'] = 1.0
            
            processed_data[symbol] = df_signals

        backtest_res = strategy.run_backtest(processed_data)
        trades = backtest_res.get('trades', [])
        
        if not trades:
            results_list.append({
                'Threshold': t, 'Trades': 0, 'Win Rate': 0, 'Net PnL': 0, 
                'Profit Factor': 0, 'Sharpe Ratio': 0, 'Max Drawdown': 0
            })
            continue

        trades_df = pd.DataFrame([vars(trade) for trade in trades])
        pnl = trades_df['pnl'].sum()
        win_rate = trades_df['win'].mean()
        
        # Calculate other metrics
        winning_trades = trades_df[trades_df['pnl'] > 0]['pnl'].sum()
        losing_trades = abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum())
        profit_factor = winning_trades / losing_trades if losing_trades != 0 else np.inf
        
        # Simple Sharpe (assuming daily)
        returns = trades_df['pnl']
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0
        
        # Drawdown
        cum_pnl = trades_df['pnl'].cumsum()
        drawdown = (cum_pnl.cummax() - cum_pnl).max()

        results_list.append({
            'Threshold': t,
            'Trades': len(trades_df),
            'Win Rate': win_rate * 100,
            'Net PnL': pnl,
            'Profit Factor': profit_factor,
            'Sharpe Ratio': sharpe,
            'Max Drawdown': drawdown
        })

    # Sort and Print
    results_df = pd.DataFrame(results_list).sort_values(by='Net PnL', ascending=False)
    print(results_df.to_string(index=False))
    
    best = results_df.iloc[0]
    print("\nBest Threshold:")
    print(f"Threshold: {best['Threshold']:.2f}")
    print(f"Trades: {best['Trades']}")
    print(f"Win Rate: {best['Win Rate']:.2f}%")
    print(f"Net PnL: ${best['Net PnL']:.2f}")
    print(f"Profit Factor: {best['Profit Factor']:.2f}")

if __name__ == '__main__':
    import numpy as np
    run_optimization()
