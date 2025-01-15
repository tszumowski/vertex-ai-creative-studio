FROM python:3.12-slim

WORKDIR /api_gateway

# Copy the common directory 
COPY ./common ./common 

# Install the common dependencies
RUN pip install --no-cache-dir -r ./common/requirements.txt

# Copy the service's requirements file
COPY ./api_gateway/requirements.txt .

# Install the service-specific dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service's code
COPY ./api_gateway . 

# Expose the service's port
EXPOSE 8000

# Command to run the service (replace with your actual command)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]