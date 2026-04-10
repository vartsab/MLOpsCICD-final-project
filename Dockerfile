FROM python:3.11-slim

WORKDIR /app

# Prevent Python from buffering stdout/stderr, useful for container logs
ENV PYTHONUNBUFFERED=1

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY app ./app
COPY model ./model

# Expose FastAPI port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
