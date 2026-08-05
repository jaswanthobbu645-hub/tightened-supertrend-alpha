import pandas as pd
import numpy as np
import joblib
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

def get_data():
    df = pd.read_csv('training_data.csv')
    feature_cols = ['ema200_trend','ema50_trend','adx','hurst','garch_vol','atr_pct','volume_ratio','st_fast_dir','st_slow_dir','rsi','ema20_slope','ema50_slope','ema200_slope','macd_hist','momentum20','momentum50','market_regime']
    X = df[feature_cols]
    y = df['target']
    return X, y, feature_cols

def run_pipeline():
    X, y, feature_cols = get_data()
    
    models = {
        'LogisticRegression': (LogisticRegression(solver='liblinear'), True),
        'RandomForest': (RandomForestClassifier(n_estimators=100, random_state=42), False),
        'XGBoost': (xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42), False)
    }
    
    results = {}
    best_model_name = "LogisticRegression"
    best_score = -1
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    for name, (model, use_scaler) in models.items():
        if use_scaler:
            X_data = StandardScaler().fit_transform(X)
        else:
            X_data = X.values
            
        scoring = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
        scores = cross_validate(model, X_data, y, cv=cv, scoring=scoring)
        
        mean_roc = np.mean(scores['test_roc_auc'])
        std_roc = np.std(scores['test_roc_auc'])
        
        results[name] = {
            'mean_roc': mean_roc,
            'std_roc': std_roc,
            'accuracy': np.mean(scores['test_accuracy']),
            'precision': np.mean(scores['test_precision']),
            'recall': np.mean(scores['test_recall']),
            'f1': np.mean(scores['test_f1'])
        }
        
        print(f"--- {name} ---")
        print(f"Mean ROC-AUC: {mean_roc:.4f} (+/- {std_roc:.4f})")
        
        if mean_roc > best_score:
            best_score = mean_roc
            best_model_name = name
            
        if name in ['RandomForest', 'XGBoost']:
            model.fit(X_data, y)
            importances = pd.DataFrame({'feature': feature_cols, 'importance': model.feature_importances_})
            print("Sorted Feature Importance:")
            print(importances.sort_values(by='importance', ascending=False).to_string(index=False))
            print()

    print(f"Best model selected: {best_model_name} with ROC-AUC {best_score:.4f}")
    
    # Final saving
    best_model_info = models[best_model_name]
    if best_model_info[1]: # Needs scaler
        scaler = StandardScaler()
        X_final = scaler.fit_transform(X)
        joblib.dump(scaler, 'scaler.pkl')
    else:
        X_final = X
        
    model = best_model_info[0]
    model.fit(X_final, y)
    joblib.dump(model, 'best_model.pkl')
    joblib.dump(best_model_name, 'model_meta.pkl')
    
    # Save performance for backtest report
    import json
    with open('model_performance.json', 'w') as f:
        json.dump(results[best_model_name], f)

if __name__ == '__main__':
    run_pipeline()
