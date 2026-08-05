import pandas as pd
import numpy as np
import sys
import os

# Add the project root to sys.path to import the module
sys.path.append(os.path.abspath('./src'))

# Assuming the class TightenedSuperTrend is in src/strategy.py
# Since it's in src/strategy.py, we need to import from src.strategy
from strategy import TightenedSuperTrend

def test_supertrend():
    # Create dummy data
    data = {
        'high': [10, 11, 12, 11, 10, 9, 8, 9, 10, 11],
        'low': [8, 9, 10, 9, 8, 7, 6, 7, 8, 9],
        'close': [9, 10, 11, 10, 9, 8, 7, 8, 9, 10]
    }
    df = pd.DataFrame(data)
    
    st = TightenedSuperTrend(symbols=['BTC'])
    st_line, st_dir = st.calculate_supertrend(df, period=3, multiplier=2.0)
    
    print("ST Line:", st_line)
    print("ST Dir:", st_dir)
    
    assert len(st_line) == len(df)
    assert len(st_dir) == len(df)
    print("Verification passed!")

if __name__ == "__main__":
    try:
        test_supertrend()
    except Exception as e:
        print(f"Verification failed: {e}")
        sys.exit(1)
