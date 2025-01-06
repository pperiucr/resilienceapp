# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the server code to the container
COPY ResilienceCombination.py /app/

# Install dependencies (including pyzmq)
# Copy the requirements file (if exists) and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose the ZMQ server port
EXPOSE 5550

# Set environment variable for port
ENV RESC_PORT=5550

# Command to run the ZMQ server
CMD ["python", "ResilienceCombination.py"]
