FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY auth.py .
COPY config.py .
COPY database.py .
COPY .env .

# Expose port
EXPOSE 7860

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "2", "app:app"]
