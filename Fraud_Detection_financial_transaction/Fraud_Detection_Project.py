# """
# Fraud Detection (Expanded)
# - Works with sample transactions.csv (numeric + 'type' categorical)
# - Produces alerts.csv used by dashboard
# """
import os, warnings
import numpy as np, pandas as pd, joblib
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
warnings.filterwarnings('ignore')
np.random.seed(42)

def load_data(path='transactions.csv'):
    df = pd.read_csv(path)
    print("Loaded", df.shape, "transactions")
    return df

def preprocess(df):
    df = df.copy()
    # One-hot encode 'type'
    if 'type' in df.columns:
        df = pd.get_dummies(df, columns=['type'], drop_first=True)
    X = df.select_dtypes(include=[np.number]).fillna(0)
    # drop label if present
    if 'label' in X.columns:
        X = X.drop(columns=['label'])
    scaler = StandardScaler()
    Xs = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)
    return Xs, scaler, df

def isolation_forest_detector(X, contamination=0.02):
    iso = IsolationForest(n_estimators=200, contamination=contamination, random_state=42)
    iso.fit(X)
    scores = -iso.decision_function(X)  # higher = more anomalous
    preds = iso.predict(X)  # -1 anomaly, 1 normal
    preds = np.where(preds == -1, 1, 0)
    return preds, scores, iso

def save_alerts(df_original, flags, scores, outname='alerts.csv'):
    df = df_original.copy().reset_index(drop=True)
    df['is_anomaly'] = flags
    df['anomaly_score'] = scores
    df['acknowledged'] = 0
    df['snoozed_until'] = ''
    df[df['is_anomaly']==1].sort_values('anomaly_score', ascending=False).to_csv(outname, index=False)
    print("Saved alerts to", outname)

def run(path='transactions.csv'):
    df = load_data(path)
    X, scaler, df_orig = preprocess(df)
    flags, scores, iso = isolation_forest_detector(X, contamination=0.02)
    save_alerts(df_orig, flags, scores, outname='alerts.csv')
    os.makedirs('artifacts', exist_ok=True)
    joblib.dump(iso, 'artifacts/isolation_forest.joblib')
    joblib.dump(scaler, 'artifacts/scaler.joblib')
    print("Done. Alerts saved and artifacts written.")

if __name__ == '__main__':
    run('transactions.csv')
