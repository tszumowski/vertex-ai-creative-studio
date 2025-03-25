# Copyright 2025 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM python:3.12-slim

WORKDIR /app

# Copy the common directory 
COPY ./common ./common 

# Install the common dependencies
RUN pip install --no-cache-dir -r ./common/requirements.txt

# Copy the service's requirements file
COPY ./generation_service/requirements.txt .

# Install the service-specific dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service's code 
COPY ./generation_service . 

# Expose the service's port
EXPOSE 8080

# Command to run the service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]