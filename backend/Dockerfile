# Dockerfile

# Use the official lightweight Python image.
FROM python:3.9-slim

# Set environment variables to prevent Python from writing pyc files and to buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY app.py main.py db_models.py ./

# Expose the port Flask runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "main.py"]
