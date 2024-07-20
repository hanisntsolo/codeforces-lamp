# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and templates into the container
COPY codeforces-lamp.py codeforces-lamp.py
# Ensure the environment variables are sourced

# Expose the port the app runs on
EXPOSE 5008

# Run the application
CMD ["python", "codeforces-lamp.py"]
