FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Set working directory
WORKDIR /app

# Copy pre-downloaded packages
COPY ./therapist_backend_v2/Lib/site-packages /packages

# Copy only the requirements file first to leverage Docker cache
COPY ./app/requirements.txt /app/requirements.txt

# Install dependencies from local directory
RUN pip install --no-index --find-links=/packages -r /app/requirements.txt

# Copy the application code
COPY ./app /app

# Copy the model files
COPY ./app/data/training_data.jsonl /app/data/training_data.jsonl

# Set the command to run the FastAPI application
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:80", "--workers", "4"]