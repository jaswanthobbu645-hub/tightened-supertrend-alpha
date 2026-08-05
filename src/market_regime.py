import pandas as pd
import numpy as np

def detect_market_regime(df: pd.DataFrame) -> np.ndarray:
    """
    Detects market regimes based on indicators:
    0 = RANGING
    1 = TRENDING
    2 = VOLATILITY_EXPANSION
    3 = VOLATILITY_COMPRESSION
    """
    # Initialize regime array
    regime = np.zeros(len(df))
    
    # Pre-calculate conditions
    adx_trending = df['adx'] > 25
    hurst_trending = df['hurst'] > 0.55
    
    # Trend detection: ADX and EMA slopes
    # Using EMA slopes to confirm direction
    ema_trend = (
        (df['ema20_slope'] > 0) & (df['ema50_slope'] > 0) & (df['ema200_slope'] > 0)
    ) | (
        (df['ema20_slope'] < 0) & (df['ema50_slope'] < 0) & (df['ema200_slope'] < 0)
    )
    
    trending = adx_trending & ema_trend
    
    # Volatility detection
    # Compare ATR% to its own MA to detect changes
    atr_ma = df['atr_pct'].rolling(window=20).mean()
    vol_expansion = df['atr_pct'] > (atr_ma * 1.2)
    vol_compression = df['atr_pct'] < (atr_ma * 0.8)
    
    # Prioritize volatile regimes over trending/ranging
    regime[vol_expansion.values] = 2
    regime[vol_compression.values] = 3
    
    # Apply Trend/Ranging on top of non-volatile states
    # Default is 0 (Ranging)
    mask_stable = (regime == 0)
    regime[mask_stable & trending.values] = 1
    
    return regime
