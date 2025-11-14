# Simple Dockerfile for the Flask dashboard
FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements-deploy.txt
EXPOSE 5001
CMD ["python", "app_flask_dashboard.py"]
