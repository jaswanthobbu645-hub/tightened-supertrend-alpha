import pandas as pd
import os
import joblib
import numpy as np
import json
from src.strategy import TightenedSuperTrend

def run():
    model = joblib.load('best_model.pkl')
    model_name = joblib.load('model_meta.pkl')
    scaler = joblib.load('scaler.pkl') if os.path.exists('scaler.pkl') else None
    
    with open('model_performance.json', 'r') as f:
        perf = json.load(f)

    symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT']
    data_dir = 'data'
    data = {}
    
    for symbol in symbols:
        file_path = os.path.join(data_dir, f'{symbol}.csv')
        if os.path.exists(file_path):
            data[symbol] = pd.read_csv(file_path, index_col='timestamp', parse_dates=True)

    if not data:
        return

    strategy = TightenedSuperTrend(symbols=symbols, adx_threshold=30.0)

    processed_data = {}
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
            'momentum50': df_signals['momentum50'],
            'market_regime': df_signals['market_regime'],
        }

        feat_df = pd.DataFrame(feature_cols_map).fillna(0)
        if scaler:
            feat_df = scaler.transform(feat_df)
            
        df_signals['prob_win'] = model.predict_proba(feat_df)[:, 1]
        
        # Sizing rules
        def get_size(p):
            if p >= 0.80: return 1.0
            if p >= 0.65: return 0.5
            return 0.0

        df_signals['size_factor'] = df_signals['prob_win'].apply(get_size)
        
        mask = (df_signals['size_factor'] > 0)
        df_signals['long_signal'] = (df_signals['long_signal'] == True) & mask
        df_signals['short_signal'] = False
        df_signals['long_size_factor'] = df_signals['size_factor']
        df_signals['short_size_factor'] = 0.0
        
        processed_data[symbol] = df_signals

    results = strategy.run_backtest(processed_data)
    trades_df = pd.DataFrame([vars(t) for t in results.get('trades', [])])
    
    if not trades_df.empty:
        # Metrics Calculation
        total_trades = len(trades_df)
        win_rate = (trades_df['win'].mean() * 100)
        net_pnl = trades_df['pnl'].sum()
        
        profits = trades_df[trades_df['pnl'] > 0]['pnl'].sum()
        losses = abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum())
        profit_factor = profits / losses if losses != 0 else float('inf')
        
        # Sharpe Ratio (assuming daily, this is rough)
        sharpe = (trades_df['pnl'].mean() / trades_df['pnl'].std()) * np.sqrt(252) if trades_df['pnl'].std() != 0 else 0
        
        # Max Drawdown
        cum_pnl = trades_df['pnl'].cumsum()
        running_max = cum_pnl.cummax()
        # Ensure base is consistent for drawdown calculation
        base_equity = 10000 
        drawdowns = (cum_pnl - running_max) / (base_equity + running_max)
        max_drawdown = drawdowns.min()
        
        # New Metrics
        # Sortino Ratio (Downside deviation)
        negative_returns = trades_df[trades_df['pnl'] < 0]['pnl']
        downside_std = negative_returns.std() if len(negative_returns) > 0 else 0
        sortino = (trades_df['pnl'].mean() / downside_std) * np.sqrt(252) if downside_std != 0 else 0
        
        # Calmar Ratio
        # Annualized return (using PnL sum, rough proxy for now)
        annualized_return = net_pnl * (252 / total_trades) if total_trades > 0 else 0
        calmar = (annualized_return / abs(max_drawdown * base_equity)) if max_drawdown != 0 else 0
        
        # Expectancy
        win_rate_decimal = win_rate / 100
        avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if profits > 0 else 0
        avg_loss = abs(trades_df[trades_df['pnl'] < 0]['pnl'].mean()) if losses > 0 else 0
        expectancy = (win_rate_decimal * avg_win) - ((1 - win_rate_decimal) * avg_loss)
        
        # Recovery Factor
        recovery_factor = net_pnl / abs(max_drawdown * base_equity) if max_drawdown != 0 else 0
        
        print("==============================")
        print("FINAL PERFORMANCE REPORT")
        print("==============================")
        print("")
        print(f"Total Trades: {total_trades}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Net Profit: ${net_pnl:.2f}")
        print(f"Profit Factor: {profit_factor:.2f}")
        print(f"Sharpe Ratio: {sharpe:.2f}")
        print(f"Sortino Ratio: {sortino:.2f}")
        print(f"Calmar Ratio: {calmar:.2f}")
        print(f"Recovery Factor: {recovery_factor:.2f}")
        print(f"Expectancy: {expectancy:.2f}")
        print(f"Maximum Drawdown: {max_drawdown*100:.2f}%")
        print("")
        print("==============================")
    else:
        print("--- Final Report ---")
        print("Trades: 0")

if __name__ == '__main__':
    run()
