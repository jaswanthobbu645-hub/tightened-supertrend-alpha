import itertools
import pandas as pd
import numpy as np
import os
import tqdm
import csv
import sys
from src.strategy import TightenedSuperTrend
import time

# Configuration
symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT']
data_dir = 'data'
data = {}
results_file = 'parameter_results.csv'

# Debug function
def debug(msg):
    sys.stdout.write(f"[DEBUG] {msg}\n")
    sys.stdout.flush()

# Load data
print("[1] Loading data...", flush=True)
for symbol in symbols:
    file_path = os.path.join(data_dir, f'{symbol}.csv')
    if os.path.exists(file_path):
        data[symbol] = pd.read_csv(file_path, index_col='timestamp', parse_dates=True)
print("[2] Data loaded", flush=True)

if not data:
    print("No data found in data directory.")
    exit(1)

# Grid Parameters
fast_period = [7, 10, 14]
fast_mult = [2.0, 2.5, 3.0]
slow_period = [20, 30]
slow_mult = [3.0, 4.0]
adx_threshold = [20, 25, 30]
garch_sl_mult = [1.5, 2.0]
garch_tp_mult = [3.0, 4.0]

param_combinations = list(itertools.product(
    fast_period, fast_mult, slow_period, slow_mult, adx_threshold, garch_sl_mult, garch_tp_mult
))

# Load existing results to skip
completed_params = set()
best_net_pnl = -float('inf')

if os.path.exists(results_file) and os.path.getsize(results_file) > 0:
    existing_df = pd.read_csv(results_file)
    best_net_pnl = existing_df['Net PnL'].max()
    param_cols = ['Fast Period', 'Fast Mult', 'Slow Period', 'Slow Mult', 'ADX', 'SL', 'TP']
    for _, row in existing_df.iterrows():
        completed_params.add(tuple(row[param_cols]))
    print(f"Resuming: {len(completed_params)} combinations already completed.")
else:
    print("No existing results file or empty file. Starting fresh.")

# Prepare CSV for writing
header = ['Fast Period', 'Fast Mult', 'Slow Period', 'Slow Mult', 'ADX', 'SL', 'TP',
          'Trades', 'Win Rate', 'Net PnL', 'Profit Factor', 'Sharpe Ratio', 'Max Drawdown']

file_exists = os.path.exists(results_file)

with open(results_file, 'a', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=header)
    if not file_exists:
        writer.writeheader()

    total_combinations = len(param_combinations)
    start_time = time.time()
    
    # Progress Loop - MODIFIED to run only one iteration
    pbar = tqdm.tqdm(param_combinations, initial=len(completed_params), total=total_combinations)
    
    iteration_count = 0
    for params in pbar:
        # Debug: Before parameter combination
        print(f"[3] Testing params: {params}", flush=True)
        
        if iteration_count >= 1:
            debug("Finished 1 iteration. Stopping.")
            break
            
        fp, fm, sp, sm, adx, sl, tp = params
        
        # Skip if already done
        if params in completed_params:
            continue
            
        iteration_count += 1
        
        # Calculate ETA
        elapsed = time.time() - start_time
        done = len(completed_params)
        if done > 0:
            remaining = (total_combinations - done) * (elapsed / done)
            eta_str = f"{remaining/60:.1f}m"
        else:
            eta_str = "Calculating..."
        
        pbar.set_description(f"Best Net PnL: ${best_net_pnl:.2f} | ETA: {eta_str}")
        
        # Debug: Before strategy creation
        print("[4] Creating strategy", flush=True)
        strategy = TightenedSuperTrend(
            symbols=symbols,
            fast_period=fp,
            fast_mult=fm,
            slow_period=sp,
            slow_mult=sm,
            adx_threshold=adx,
            garch_sl_mult=sl,
            garch_tp_mult=tp
        )
        # Debug: After strategy creation
        print("[5] Strategy created", flush=True)
        
        processed_data = {}
        for symbol, df in data.items():
            # Debug: Before generate_signals
            print(f"[6] generate_signals {symbol}", flush=True)
            processed_data[symbol] = strategy.generate_signals(df)
            # Debug: After generate_signals
            print(f"[7] Finished {symbol}", flush=True)
            
        # Debug: Before backtest
        print("[8] Starting backtest", flush=True)
        backtest_results = strategy.run_backtest(processed_data)
        # Debug: After backtest
        print("[9] Backtest finished", flush=True)
        
        trades = backtest_results.get('trades', [])
        
        if trades:
            trades_df = pd.DataFrame([vars(t) for t in trades])
            total_trades = len(trades_df)
            win_rate = (trades_df['win'].mean() * 100)
            net_pnl = trades_df['pnl'].sum()
            profits = trades_df[trades_df['pnl'] > 0]['pnl'].sum()
            losses = abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum())
            profit_factor = profits / losses if losses != 0 else float('inf')
            sharpe = (trades_df['pnl'].mean() / trades_df['pnl'].std()) * np.sqrt(252) if trades_df['pnl'].std() != 0 else 0
            cum_pnl = trades_df['pnl'].cumsum()
            running_max = cum_pnl.cummax()
            drawdown = (cum_pnl - running_max) / (running_max + 10000)
            max_drawdown = drawdown.min() * 100
        else:
            total_trades, win_rate, net_pnl, profit_factor, sharpe, max_drawdown = 0, 0, 0, 0, 0, 0
        
        # Update best
        if net_pnl > best_net_pnl:
            best_net_pnl = net_pnl
        
        # Write to CSV
        # Debug: Before CSV write
        print("[10] Writing CSV", flush=True)
        writer.writerow({
            'Fast Period': fp, 'Fast Mult': fm, 'Slow Period': sp, 'Slow Mult': sm,
            'ADX': adx, 'SL': sl, 'TP': tp,
            'Trades': total_trades, 'Win Rate': win_rate, 'Net PnL': net_pnl,
            'Profit Factor': profit_factor, 'Sharpe Ratio': sharpe, 'Max Drawdown': max_drawdown
        })
        f.flush()
        os.fsync(f.fileno())
        # Debug: After CSV write
        print("[11] CSV written", flush=True)
        
        completed_params.add(params)
