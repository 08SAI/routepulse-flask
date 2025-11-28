# Use a small official Python base
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Expose the port the app listens on
EXPOSE 12104

# Run the Flask app
CMD ["python", "app.py"]
