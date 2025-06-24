# Use official Python base image
FROM python:3.11-slim

# Set working dir
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose your Django port
EXPOSE 3004

# Start the Django dev server
ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:3004"]
