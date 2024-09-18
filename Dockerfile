# Use the official Python image as a base
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy all the files from the host to /app in the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements_.txt

# Expose the port the app runs on
EXPOSE 8081

# Run the FastAPI app
CMD ["uvicorn", "weather_predict_api:app", "--host", "0.0.0.0", "--port", "8081"]
