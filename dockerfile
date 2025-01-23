FROM python:3.8.20-slim

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Command to run migrations
CMD ["sh", "-c", "alembic upgrade head"]

# Expose the application port
EXPOSE 8000
WORKDIR /app/users
# Command to run Celery and FastAPI
CMD ["sh", "-c", "celery -A celery_app worker --loglevel=info --pool=solo & celery -A celery_app beat --loglevel=info & uvicorn main:app --host 0.0.0.0 --port 8000"]