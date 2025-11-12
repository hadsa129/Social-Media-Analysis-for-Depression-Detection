FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install NLTK data
RUN python -m nltk.downloader punkt stopwords

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["uvicorn", "api_nett.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]