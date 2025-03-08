resource "google_project_service" "iap_service" {
  project = var.project_id
  service = "iap.googleapis.com"
}

resource "google_iap_client" "default" {
  display_name = "Genmedia Studio Client"
  brand        =  "projects/${var.project_id}/brands/${var.iap_brand_id}"
}

resource "google_project_service_identity" "iap_sa" {
  provider = google-beta
  project  = google_project_service.iap_service.project
  service  = "iap.googleapis.com"
}