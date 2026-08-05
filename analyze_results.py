import pandas as pd
import numpy as np

def calculate_stats(trades_df):
    trades_df['pnl'] = trades_df['pnl'].fillna(0)
    total_pnl = trades_df['pnl'].sum()
    num_trades = len(trades_df)
    win_rate = (trades_df['win'].mean()) * 100
    
    # Simple profit factor: sum of winning trades / sum of absolute losing trades
    wins = trades_df[trades_df['pnl'] > 0]['pnl'].sum()
    losses = abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum())
    profit_factor = wins / losses if losses != 0 else np.inf
    
    # Sharpe Ratio (approx)
    sharpe = (trades_df['pnl'].mean() / trades_df['pnl'].std()) * np.sqrt(252)
    
    # Max Drawdown
    # Need to simulate equity curve
    return {
        'total_trades': num_trades,
        'win_rate': win_rate,
        'net_pnl': total_pnl,
        'profit_factor': profit_factor,
        'sharpe': sharpe
    }

for symbol in ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT']:
    df = pd.read_csv(f'{symbol}_trades.csv')
    stats = calculate_stats(df)
    print(f"{symbol} stats: {stats}")
