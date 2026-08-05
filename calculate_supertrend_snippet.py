    def calculate_supertrend(
        self, 
        df: pd.DataFrame, 
        period: int, 
        multiplier: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate standard SuperTrend indicator
        
        Returns:
            st_line: SuperTrend line values
            st_dir: Direction (1 = bullish, -1 = bearish)
        """
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        n = len(close)

        # True Range
        tr = np.zeros(n)
        tr[0] = high[0] - low[0]
        for i in range(1, n):
            tr[i] = max(
                high[i] - low[i],
                abs(high[i] - close[i-1]),
                abs(low[i] - close[i-1])
            )
        
        # ATR
        atr = np.zeros(n)
        atr[period-1] = np.mean(tr[:period])
        for i in range(period, n):
            atr[i] = (atr[i-1] * (period - 1) + tr[i]) / period

        # Basic Upper/Lower Bands
        hl2 = (high + low) / 2
        upper_band = hl2 + (multiplier * atr)
        lower_band = hl2 - (multiplier * atr)
        
        st_line = np.zeros(n)
        st_dir = np.zeros(n) # 1 for uptrend, -1 for downtrend
        
        # Initialization
        st_line[0] = upper_band[0]
        st_dir[0] = 1 # Start with uptrend assumption
        
        for i in range(1, n):
            # Update bands
            if close[i-1] > st_line[i-1]:
                upper_band[i] = min(upper_band[i], st_line[i-1])
                lower_band[i] = lower_band[i]
            else:
                upper_band[i] = upper_band[i]
                lower_band[i] = max(lower_band[i], st_line[i-1])
            
            # Decide trend
            if close[i] > upper_band[i]:
                st_dir[i] = 1
                st_line[i] = lower_band[i]
            elif close[i] < lower_band[i]:
                st_dir[i] = -1
                st_line[i] = upper_band[i]
            else:
                st_dir[i] = st_dir[i-1]
                st_line[i] = st_line[i-1]
                
        return st_line, st_dir
