# 
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory into the container's current working directory (/app)
COPY . .

# Disable Python output buffering, so logs and print statements appear immediately
ENV PYTHONUNBUFFERED=1

# Default command to run when the container starts which is to launch FastAPI server
CMD ["python", "app.py"]
