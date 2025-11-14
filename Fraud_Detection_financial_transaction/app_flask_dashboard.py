# """
# Flask dashboard to view and manage alerts (supports acknowledge and snooze)
# Run:
#     python app_flask_dashboard.py
# Open: http://127.0.0.1:5001
# """
from flask import Flask, render_template, request, redirect, jsonify
import pandas as pd, os, datetime, csv

app = Flask(__name__)

ALERTS_PATH = 'alerts.csv'

def read_alerts():
    if os.path.exists(ALERTS_PATH):
        df = pd.read_csv(ALERTS_PATH, parse_dates=['snoozed_until'], keep_default_na=False)
    else:
        df = pd.DataFrame()
    return df

def write_alerts(df):
    df.to_csv(ALERTS_PATH, index=False)

@app.route("/")
def index():
    df = read_alerts()
    if df.empty:
        alerts = []
    else:
        # filter out snoozed (if snoozed_until in future)
        now = pd.Timestamp.now()
        def is_active(row):
            if row.get('is_anomaly',0) != 1: return False
            if row.get('acknowledged',0) == 1: return False
            su = row.get('snoozed_until','')
            if pd.isna(su) or su=='':
                return True
            try:
                return pd.to_datetime(su) <= now
            except Exception:
                return True
        active = df[df.apply(is_active, axis=1)].sort_values('anomaly_score', ascending=False).head(200)
        alerts = active.to_dict(orient='records')
    # summary stats
    total_alerts = len(df[df['is_anomaly']==1]) if not df.empty else 0
    unack = len([r for r in alerts])
    return render_template('dashboard.html', alerts=alerts, total_alerts=total_alerts, unack=unack)

@app.route("/acknowledge", methods=['POST'])
def acknowledge():
    tx_id = request.form.get('transaction_id')
    if not tx_id:
        return redirect('/')
    df = read_alerts()
    if df.empty:
        return redirect('/')
    df.loc[df['transaction_id'].astype(str)==str(tx_id),'acknowledged'] = 1
    write_alerts(df)
    return redirect('/')

@app.route("/snooze", methods=['POST'])
def snooze():
    tx_id = request.form.get('transaction_id')
    minutes = int(request.form.get('minutes', 60))
    if not tx_id:
        return redirect('/')
    df = read_alerts()
    if df.empty:
        return redirect('/')
    until = pd.Timestamp.now() + pd.Timedelta(minutes=minutes)
    df.loc[df['transaction_id'].astype(str)==str(tx_id),'snoozed_until'] = until.isoformat()
    write_alerts(df)
    return redirect('/')

@app.route("/api/alerts")
def api_alerts():
    df = read_alerts()
    return df.to_json(orient='records')

if __name__ == '__main__':
    app.run(port=5001, debug=True)
