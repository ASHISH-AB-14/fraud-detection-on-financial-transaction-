# Expanded Fraud Detection Package - Deployment Notes

## Files added
- `transactions.csv` (sample synthetic data)
- `Fraud_Detection_Project.py` (pipeline script)
- `app_flask_dashboard.py` (dashboard with acknowledge/snooze)
- `templates/dashboard.html`
- `requirements-deploy.txt` (lighter deps for dashboard)
- `Dockerfile` (container for dashboard)

## Quickstart
1. Install deps:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\\Scripts\\activate on Windows
   pip install -r requirements-deploy.txt
   ```
2. Run pipeline to generate `alerts.csv`:
   ```bash
   python Fraud_Detection_Project.py
   ```
3. Start dashboard:
   ```bash
   python app_flask_dashboard.py
   ```
   Open http://127.0.0.1:5001

## Docker
Build image:
```
docker build -t fraud-dashboard:latest .
```
Run container:
```
docker run -p 5001:5001 fraud-dashboard:latest
```

## Notes
- `app_flask_dashboard.py` supports acknowledging and snoozing alerts; these update `alerts.csv` in-place.
