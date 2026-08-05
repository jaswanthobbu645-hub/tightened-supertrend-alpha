import pandas as pd
import glob
import os

def analyze_trades():
    files = ['BTCUSDT_trades.csv', 'ETHUSDT_trades.csv', 'SOLUSDT_trades.csv', 'BNBUSDT_trades.csv']
    dfs = []
    
    for f in files:
        if os.path.exists(f):
            df = pd.read_csv(f)
            dfs.append(df)
            
    if not dfs:
        print("No trade files found.")
        return

    full_df = pd.concat(dfs, ignore_index=True)

    def print_stats(df, title):
        print(f"\n--- {title} ---")
        total_trades = len(df)
        if total_trades == 0:
            print("No trades.")
            return
        win_rate = df['win'].mean() * 100
        net_pnl = df['pnl'].sum()
        avg_pnl = df['pnl'].mean()
        avg_bars = df['bars_held'].mean()
        
        print(f"Total trades: {total_trades}")
        print(f"Win rate: {win_rate:.2f}%")
        print(f"Net PnL: {net_pnl:.2f}")
        print(f"Average PnL: {avg_pnl:.2f}")
        print(f"Average holding bars: {avg_bars:.2f}")

    # Overall
    print_stats(full_df, "Overall Stats")

    # Per symbol
    print("\n--- Per Symbol ---")
    for symbol in full_df['symbol'].unique():
        sub = full_df[full_df['symbol'] == symbol]
        print(f"{symbol}: Trades={len(sub)}, WinRate={sub['win'].mean()*100:.2f}%, NetPnL={sub['pnl'].sum():.2f}, AvgPnL={sub['pnl'].mean():.2f}")

    # Exit reason
    print("\n--- Exit Reason Analysis ---")
    exit_counts = full_df.groupby('exit_reason').size()
    print(exit_counts)

    # Long vs Short
    print("\n--- Long vs Short ---")
    for side in ['LONG', 'SHORT']:
        sub = full_df[full_df['side'] == side]
        print(f"{side}: Trades={len(sub)}, WinRate={sub['win'].mean()*100:.2f}%, NetPnL={sub['pnl'].sum():.2f}")

if __name__ == "__main__":
    analyze_trades()
