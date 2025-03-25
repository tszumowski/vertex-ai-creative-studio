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

resource "google_artifact_registry_repository" "genmedia_studio" {
  location = var.region
  repository_id = "genmedia-studio"
  format = "DOCKER"
}

import {
  to = google_artifact_registry_repository.genmedia_studio
  id = "projects/${var.project_id}/locations/${var.region}/repositories/genmedia-studio"
}

data "google_artifact_registry_docker_image" "app" {
  location      = google_artifact_registry_repository.genmedia_studio.location
  repository_id = google_artifact_registry_repository.genmedia_studio.repository_id
  image_name    = "app:latest"
}

data "google_artifact_registry_docker_image" "generation_service" {
  location      = google_artifact_registry_repository.genmedia_studio.location
  repository_id = google_artifact_registry_repository.genmedia_studio.repository_id
  image_name    = "generation-service:latest"
}

data "google_artifact_registry_docker_image" "file_service" {
  location      = google_artifact_registry_repository.genmedia_studio.location
  repository_id = google_artifact_registry_repository.genmedia_studio.repository_id
  image_name    = "file-service:latest"
}

data "google_artifact_registry_docker_image" "api_gateway" {
  location      = google_artifact_registry_repository.genmedia_studio.location
  repository_id = google_artifact_registry_repository.genmedia_studio.repository_id
  image_name    = "api-gateway:latest"
}