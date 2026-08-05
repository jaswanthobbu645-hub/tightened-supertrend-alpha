import numpy as np
import pandas as pd

def calculate_hurst(prices, window=100):
    """
    Calculates the Hurst exponent for a given price series.
    Returns the Hurst exponent.
    """
    if len(prices) < window:
        return np.nan
    
    lags = range(2, 20)
    tau = []
    
    for lag in lags:
        # Calculate the absolute difference of the series at lag
        pp = np.subtract(prices[lag:], prices[:-lag])
        tau.append(np.sqrt(np.std(pp)))
    
    # Use polyfit to estimate the Hurst exponent (H)
    m = np.polyfit(np.log(lags), np.log(tau), 1)
    hurst = m[0] * 2.0
    return hurst

# Test
if __name__ == "__main__":
    # Random walk
    data = np.cumsum(np.random.randn(1000)) + 100
    h = calculate_hurst(data)
    print(f"Hurst exponent: {h}")
