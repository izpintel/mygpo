# Dockerfile
FROM python:3.8

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libwebp-dev \
    build-essential \
    python3-dev \
    virtualenv \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt requirements-dev.txt requirements-doc.txt requirements-setup.txt requirements-test.txt ./

# RUN pip install --upgrade pip
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements-dev.txt \
    && pip install --no-cache-dir -r requirements-doc.txt \
    && pip install --no-cache-dir -r requirements-setup.txt \
    && pip install --no-cache-dir -r requirements-test.txt 

# Copy the application code
COPY . .

# Entry point
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
