# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make sure cron is installed
RUN apt-get update && apt-get install -y cron

# Copy crontab file to the cron directory
COPY crontab /etc/cron.d/refresh_token_cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/refresh_token_cron && crontab /etc/cron.d/refresh_token_cron

# Create a log file for cron jobs
RUN touch /var/log/cron.log

# Expose the port on which the FastAPI app will run
EXPOSE 7000

# Start cron and FastAPI app
CMD service cron start && uvicorn app:app --host 0.0.0.0 --port 7000