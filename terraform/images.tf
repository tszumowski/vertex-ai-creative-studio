resource "google_artifact_registry_repository" "gemedia_studio" {
  location      = var.region
  repository_id = "genmedia-studio"
  description   = "Repository to host Docker images for GenMedia Studio"
  format        = "DOCKER"
}

data "google_artifact_registry_docker_image" "app" {
  location      = google_artifact_registry_repository.gemedia_studio.location
  repository_id = google_artifact_registry_repository.gemedia_studio.repository_id
  image_name    = var.app_image
}
