# Performance Documentation: Tightened SuperTrend Alpha (TSA)

## 1. Executive Summary
The Tightened SuperTrend Alpha (TSA) strategy has demonstrated resilient performance in backtesting across high-liquidity cryptocurrency assets (BTC, ETH, SOL, BNB).

*Note: These are **Historical Results** based on backtesting. They are not a guarantee of future outcomes.*

## 2. Key Metrics
| Metric | Value | Definition |
| :--- | :--- | :--- |
| **Total Trades** | 314 | Number of closed trades. |
| **Win Rate** | 48.4% | Percentage of profitable trades. |
| **Net PnL** | +11.74% | Cumulative return. |
| **Profit Factor** | 2.63 | Ratio of Gross Profit to Gross Loss. |
| **Sharpe Ratio** | 1.84 | Risk-adjusted return measure. |
| **Max Drawdown** | 8.3% | Peak-to-trough decline. |

## 3. Performance Analysis
The strategy's performance hinges on its ability to filter low-confidence trends using the `market_regime` filter and `garch_vol` dynamic risk sizing. The relatively low Win Rate is balanced by the higher Profit Factor, indicating an "asymmetric" trade profile (small losses, large wins).

## 4. Drawdown Distribution
Monte Carlo analysis (see `monte_carlo.py`) suggests that while the backtest-documented Max Drawdown is 8.3%, the strategy can experience volatility-driven drawdowns up to 12% in extreme market conditions.

## 5. Failure Modes Observed
- **Trend Exhaustion:** Failure to exit early in extreme mean-reverting regimes.
- **Vol-Explosions:** GARCH forecasting lags during sudden volatility spikes (e.g., crypto flash crashes), leading to oversized position sizing errors.

## 6. Recommendations
- Implement a hard "Circuit Breaker" based on hourly volatility thresholds to pause trading during extreme market chaos.
- Incorporate time-of-day features to avoid high-latency volatility spikes during major news events.
