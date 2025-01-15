FROM python:3.12-slim

WORKDIR /app

# Copy the common directory 
COPY ./common ./common 

# Install the common dependencies
RUN pip install --no-cache-dir -r ./common/requirements.txt

# Copy the service's requirements file
COPY ./image_generation_service/requirements.txt .

# Install the service-specific dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service's code 
COPY ./image_generation_service . 

# Expose the service's port
EXPOSE 8080

# Command to run the service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]