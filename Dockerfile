FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up user with UID 1000 (Hugging Face requirement)
RUN useradd -m -u 1000 user
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn feedparser requests python-multipart jinja2 gnewsdecoder

# Pre-download NLTK data
RUN python -m nltk.downloader punkt punkt_tab stopwords

# Copy the rest of the application files
COPY --chown=user:user . .

# Set environment variables for huggingface and python
ENV PYTHONUNBUFFERED=1 \
    PORT=7860 \
    HOME=/home/user

# Switch to the non-root user
USER user

# Create directories for data and set permissions
RUN mkdir -p /app/dashboard_app/data && chmod -R 777 /app/dashboard_app/data

# Expose Hugging Face Space port
EXPOSE 7860

# Command to run uvicorn
CMD ["uvicorn", "dashboard_app.main:app", "--host", "0.0.0.0", "--port", "7860"]
