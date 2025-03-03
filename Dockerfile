# Use a lightweight Python image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install required packages (including cron)
RUN apt-get update && apt-get install -y cron && pip install --no-cache-dir python-dotenv requests fastapi

# Copy necessary files
COPY . .

# Ensure token file persists (volume will be mounted at runtime)
RUN touch /app/access_token.json

# Set up cron job inside the container
RUN echo "0 0 * * * python /app/refresh_token.py >> /var/log/cron.log 2>&1" > /etc/cron.d/token_refresh
RUN chmod 0644 /etc/cron.d/token_refresh && crontab /etc/cron.d/token_refresh

# Start both cron and the app
CMD ["sh", "-c", "cron && tail -f /var/log/cron.log"]
