# Use official Python runtime
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Collect static files
ENV DJANGO_SETTINGS_MODULE=kutu_core.settings
RUN SECRET_KEY=dummy-build-key DATABASE_URL=postgres://dummy:dummy@localhost/dummy python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the application
CMD ["/start.sh"]
