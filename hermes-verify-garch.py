import sys
import os
import pandas as pd
import numpy as np

# Add the project root to sys.path so we can import src.strategy
sys.path.append(os.getcwd())

from src.strategy import TightenedSuperTrend

def verify_garch_implementation():
    print("Starting GARCH implementation verification...")
    
    # 1. Create synthetic data
    n_bars = 300
    np.random.seed(42)
    prices = 100 * np.exp(np.cumsum(np.random.normal(0, 0.01, n_bars)))
    data = pd.DataFrame({
        'open': prices,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': np.random.randint(1000, 5000, n_bars)
    }, index=pd.date_range('2023-01-01', periods=n_bars, freq='h'))
    
    # 2. Initialize strategy
    st = TightenedSuperTrend(symbols=['BTCUSDT'])
    
    # 3. Calculate indicators
    df_result = st.calculate_indicators(data)
    
    # 4. Verify results
    print(f"Columns in result: {df_result.columns.tolist()}")
    
    assert 'garch_vol' in df_result.columns, "garch_vol column missing"
    
    # After the window (100 bars), garch_vol should have values
    valid_vol = df_result['garch_vol'].iloc[150:]
    assert not valid_vol.isna().all(), "garch_vol is all NaN"
    assert (valid_vol >= 0).all(), "garch_vol contains negative values"
    
    print("GARCH volatility successfully calculated.")
    print(f"First 105 GARCH volatility values: {df_result['garch_vol'].iloc[100:105].values}")
    
    # 5. Check compatibility
    df_signals = st.generate_signals(data)
    assert 'long_signal' in df_signals.columns
    assert 'short_signal' in df_signals.columns
    print("Signals generated successfully.")
    
    print("Verification complete: GARCH implementation works as expected.")

if __name__ == "__main__":
    verify_garch_implementation()
