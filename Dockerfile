# Use official Python
FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Make sure your script is executable
RUN chmod +x executable.sh

# Expose your app port
EXPOSE 3004

# Use the script as the container's main process
ENTRYPOINT ["./executable.sh"]
