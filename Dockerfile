# Base image
FROM python:3.9-slim

# Set the environment variable for timezone to UTC
ENV TZ=UTC

# Set the working directory
WORKDIR /app

# Copy only requirements.txt first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the necessary ports
EXPOSE 8000

# Command to run your application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
