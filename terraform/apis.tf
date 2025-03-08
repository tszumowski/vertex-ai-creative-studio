locals {
  apis = [
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "compute.googleapis.com",
    "iamcredentials.googleapis.com",
    "logging.googleapis.com",
    "secretmanager.googleapis.com",
    "storage-api.googleapis.com",
    "storage-component.googleapis.com",
    "cloudscheduler.googleapis.com",
    "run.googleapis.com",
    "aiplatform.googleapis.com",
    "firestore.googleapis.com"
  ]
}

resource "google_project_service" "apis" {
  for_each = toset(local.apis)

  project = var.project_id
  service = each.key

  disable_on_destroy = false
  disable_dependent_services = true
}