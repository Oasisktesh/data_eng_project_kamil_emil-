# Use the official Python image as a base
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements file first to leverage Docker caching
COPY requirements2.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements2.txt

# Copy all the application files
COPY . .

# Expose the port the app runs on
EXPOSE 8081

# Run the FastAPI app
CMD ["uvicorn", "weather_predict_api:app", "--host", "0.0.0.0", "--port", "8081"]