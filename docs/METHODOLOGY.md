# Methodology Documentation: Tightened SuperTrend Alpha (TSA)

## 1. Indicator Mathematics
The core of the TSA strategy relies on a multi-factor approach.

### 1.1 SuperTrend
The SuperTrend indicator follows the formula:
$$ATR_t = \frac{(period-1) * ATR_{t-1} + TR_t}{period}$$
$$UpperBand = HL2 + (multiplier * ATR)$$
$$LowerBand = HL2 - (multiplier * ATR)$$

### 1.2 Hurst Exponent
The Hurst Exponent ($H$) determines the "trendiness" of a series:
- $H < 0.5$: Mean-reverting.
- $H = 0.5$: Random Walk.
- $H > 0.5$: Trending.

## 2. GARCH Theory
Generalized Autoregressive Conditional Heteroskedasticity (GARCH) is used to forecast volatility ($\sigma_t^2$). 
The GARCH(1,1) model is defined as:
$$\sigma_t^2 = \omega + \alpha \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2$$

## 3. Position Sizing
Position sizing is determined by the `risk_amount` and the GARCH-derived volatility:
$$StopDistance = Price * GARCH\_Vol * GARCH\_SL\_Mult$$
$$Size = RiskAmount / StopDistance$$

## 4. Market Regime Detection
Market regimes are detected via ADX, trend slope (EMA20/50/200), and RSI (see `src/market_regime.py`).

## 5. Machine Learning Pipeline
The system includes a training framework (`train_model.py`) that uses historical trades to generate a feature set (momentum, Hurst, Volatility) and train models (XGBoost/scikit-learn) to improve signal quality (`ml_predict.py`).

## 6. Backtesting Engine
The engine (`run_backtest`) iterates through symbol data:
1. **Indicator State:** Computed across all symbols.
2. **Trade Logic:** Evaluates exit conditions (TP, SL, ST Flip, Time Exit).
3. **Execution Logic:** Applies fee-adjusted edge and slippage calculation.

## 7. Monte Carlo Methodology
The `monte_carlo.py` script performs a path-based analysis of the strategy's trades to estimate the likelihood of various drawdown levels.

## 8. Failure Modes and Limitations
- The system depends heavily on stable GARCH estimation; if the series contains structural breaks, GARCH parameters may become unstable.
- The use of EMA slopes in regime detection introduces lookback lag.

## 9. Future Research
- Integration of order book data for improved slippage modeling.
- Multivariate regime detection (e.g., Hidden Markov Models).
- Deep reinforcement learning for dynamic threshold management.
