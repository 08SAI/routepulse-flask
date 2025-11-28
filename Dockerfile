# Use slim Python base
FROM python:3.11-slim

WORKDIR /app

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV FLASK_ENV=production

# Expose internal flask port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
