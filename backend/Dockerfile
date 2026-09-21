FROM python:3.11-slim

# Create a non-root app user for security
RUN useradd --create-home app
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code in backend/ to /app in the container
COPY --chown=app:app . .

EXPOSE 8000

# Switch to unprivileged user
USER app

# Point directly to main.py at root of /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]