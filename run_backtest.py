import pandas as pd
import os
import joblib
import numpy as np
import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from src.strategy import TightenedSuperTrend

def generate_report(trades_df, results, base_equity=10000):
    os.makedirs('results', exist_ok=True)
    
    # Calculations
    total_trades = len(trades_df)
    win_rate = (trades_df['win'].mean() * 100) if total_trades > 0 else 0
    net_pnl = trades_df['pnl'].sum()
    profits = trades_df[trades_df['pnl'] > 0]['pnl'].sum()
    losses = abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum())
    profit_factor = profits / losses if losses != 0 else float('inf')
    cum_pnl = trades_df['pnl'].cumsum()
    equity_curve = base_equity + cum_pnl
    drawdowns = (equity_curve - equity_curve.cummax()) / equity_curve.cummax()
    max_drawdown = drawdowns.min()
    
    # HTML Components
    fig_equity = px.line(x=trades_df.index, y=equity_curve, title='Equity Curve')
    fig_drawdown = px.area(x=trades_df.index, y=drawdowns, title='Drawdown Curve')
    fig_dist = px.histogram(trades_df['pnl'], title='Trade Distribution')
    fig_win_loss = px.pie(values=[len(trades_df[trades_df['pnl'] > 0]), len(trades_df[trades_df['pnl'] <= 0])], names=['Wins', 'Losses'], title='Win/Loss Distribution')
    
    # Save plotly charts to html strings
    equity_html = fig_equity.to_html(full_html=False, include_plotlyjs='cdn')
    drawdown_html = fig_drawdown.to_html(full_html=False, include_plotlyjs='cdn')
    dist_html = fig_dist.to_html(full_html=False, include_plotlyjs='cdn')
    win_loss_html = fig_win_loss.to_html(full_html=False, include_plotlyjs='cdn')

    # Metrics Table
    metrics = {
        'Total Trades': total_trades,
        'Win Rate': f'{win_rate:.2f}%',
        'Net Profit': f'${net_pnl:.2f}',
        'Profit Factor': f'{profit_factor:.2f}',
        'Max Drawdown': f'{max_drawdown*100:.2f}%'
    }
    
    metrics_table = pd.DataFrame(list(metrics.items()), columns=['Metric', 'Value']).to_html(index=False, classes='table table-striped')

    monte_carlo_html = ""
    if os.path.exists('results/monte_carlo_summary.json'):
        with open('results/monte_carlo_summary.json', 'r') as f:
            mc = json.load(f)
            monte_carlo_html = f"<h3>Monte Carlo Summary</h3><pre>{json.dumps(mc, indent=2)}</pre>"

    html_content = f"""
    <html>
    <head><title>Backtest Report</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
    </head>
    <body class='container'>
        <h1>Backtest Report</h1>
        <h2>Performance Metrics</h2>
        {metrics_table}
        {equity_html}
        {drawdown_html}
        {dist_html}
        {win_loss_html}
        {monte_carlo_html}
    </body>
    </html>
    """
    
    with open('results/backtest_report.html', 'w') as f:
        f.write(html_content)
    print("Report generated: results/backtest_report.html")

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
        generate_report(trades_df, results)
        print("==============================")
        print("FINAL PERFORMANCE REPORT")
        print("==============================")
        print("")
    else:
        print("--- Final Report ---")
        print("Trades: 0")

if __name__ == '__main__':
    run()
