# Architecture Documentation: Tightened SuperTrend Alpha (TSA)

## 1. System Overview
The Tightened SuperTrend Alpha (TSA) is a high-frequency algorithmic trading system designed for the digital asset markets (e.g., BTC/USDT, ETH/USDT). The system utilizes a multi-factor approach combining trend-following mechanics, volatility modeling via GARCH(1,1), and market regime filtering to manage trade entries and risk dynamically.

## 2. High-Level Architecture
The TSA system is structured as a modular quantitative framework designed for backtesting, optimization, and execution readiness. It separates market data ingestion, indicator computation, signal generation, and trade lifecycle management.

```mermaid
graph TD
    A[Market Data Ingestion] --> B[Indicator Pipeline]
    B --> C[Market Regime Detection]
    B --> D[Volatility Modeling (GARCH)]
    C --> E[Confidence Scoring]
    D --> E
    E --> F[Signal Generation]
    F --> G[Position Sizing (Risk-Adjusted)]
    G --> H[Execution/Backtest Engine]
    H --> I[Performance Metrics]
```

## 3. Component Breakdown
### 3.1 Indicator Pipeline
The indicator pipeline (see `src/strategy.py`: `calculate_indicators`) computes the core signals:
- **Dual SuperTrend:** Fast (8, 2.5) and Slow (18, 2.0).
- **GARCH Volatility:** Dynamic `garch_vol` computation.
- **Trend Indicators:** EMA200, EMA50, MACD.
- **Market State:** ADX, Hurst Exponent, Volume Filter.

### 3.2 GARCH Volatility Module
The GARCH(1,1) implementation (`calculate_garch_vol`) utilizes `arch_model` with a rolling window (default 75 bars) to forecast short-term volatility. This is crucial for dynamic stop-loss placement, replacing static ATR multiples.

### 3.3 Confidence Scoring System
A heuristic-weighted engine (`calculate_confidence_score`) that aggregates signals across different domains (Trend, ADX, Hurst, Volume, Volatility) to determine sizing.

## 4. Design Decisions
- **Modularity:** Strategies are self-contained classes.
- **Vectorized Computation:** Indicator calculation uses `numpy` for speed.
- **Backtest Loop:** Implements a time-ordered bar-by-bar simulation, allowing for accurate fill logic including slippage and commission.

## 5. Failure Modes & Limitations
- **Data Latency:** Backtest assumes zero-latency for execution.
- **Overfitting:** The dual SuperTrend and confidence scoring system may suffer from parameter sensitivity.
- **Execution Risks:** No explicit handling of limit order book depth (slippage is simplified).

## 6. Future Research
- Order flow imbalance integration.
- Latency-sensitive execution modeling.
- Reinforcement learning-based signal optimization.
