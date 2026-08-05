import joblib
import pandas as pd
import os

class ModelPredictor:
    def __init__(self):
        self.model = joblib.load('best_model.pkl')
        self.model_name = joblib.load('model_meta.pkl')
        self.scaler = joblib.load('scaler.pkl') if os.path.exists('scaler.pkl') else None
        self.feature_cols = [
            'ema200_trend', 'ema50_trend', 'adx', 'hurst', 'garch_vol', 'atr_pct',
            'volume_ratio', 'st_fast_dir', 'st_slow_dir'
        ]

    def predict(self, features):
        data = pd.DataFrame([features])[self.feature_cols]
        if self.scaler:
            data = self.scaler.transform(data)
        
        # LogisticRegression uses predict_proba, others have similar API
        prob = self.model.predict_proba(data)[0, 1]
        return prob

def predict_win_probability(features):
    predictor = ModelPredictor()
    return predictor.predict(features)

if __name__ == '__main__':
    sample = {
        'ema200_trend': 1, 'ema50_trend': 1, 'adx': 35, 'hurst': 0.6, 
        'garch_vol': 0.01, 'atr_pct': 1.5, 'volume_ratio': 1.5, 
        'st_fast_dir': 1, 'st_slow_dir': 1
    }
    print(f"Probability: {predict_win_probability(sample):.4f}")
