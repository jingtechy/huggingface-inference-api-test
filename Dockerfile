# Stage 1: Base image with dependencies
FROM python:3.11-slim AS base
# Set working directory
WORKDIR /app
# Copy dependencies and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: App image
FROM base AS app
# Copy everything except what's ignored
COPY . .
# Disable Python output buffering, so logs appear immediately
ENV PYTHONUNBUFFERED=1
# Default command to run FastAPI app when container starts
CMD ["python", "app.py"]

# Stage 3: Test image
FROM base AS test
# Copy everything except what's ignored
COPY . .
# Disable Python output buffering
ENV PYTHONUNBUFFERED=1
# Default command to run tests when container starts
CMD ["pytest", "--disable-warnings", "-q", "--junitxml=reports/junit.xml", "--html=reports/report.html", "--self-contained-html"]
