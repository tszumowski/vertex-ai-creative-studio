resource "google_artifact_registry_repository" "genmedia_studio" {
  location = var.region
  repository_id = "genmedia-studio"
  format = "DOCKER"
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