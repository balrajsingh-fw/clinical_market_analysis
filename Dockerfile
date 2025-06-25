# Use official Python
FROM python:3.11-slim


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Make sure your script is executable
COPY ./executable.sh /executable.sh
RUN chmod +x executable.sh

# Expose your app port
EXPOSE 8042

# Use the script as the container's main process
ENTRYPOINT ["./executable.sh"]
