# Service Account for the Cloud Function
resource "google_service_account" "genmedia_service_account" {
  account_id   = "genmedia"
  display_name = "GenMedia Service Account"
}

resource "google_service_account" "genmedia_service_invoker_account" {
  account_id   = "genmedia-invoker"
  display_name = "GenMedia Invoker Service Account"
}

resource "google_project_iam_binding" "genmedia_logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"

  members = [
    "serviceAccount:${google_service_account.genmedia_service_account.email}"
  ]
}

resource "google_project_iam_binding" "genmedia_logging_viewer" {
  project = var.project_id
  role    = "roles/logging.viewer"

  members = [
    "serviceAccount:${google_service_account.genmedia_service_account.email}"
  ]
}

resource "google_project_iam_binding" "genmedia_aiplatform_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"

  members = [
    "serviceAccount:${google_service_account.genmedia_service_account.email}"
  ]
}

resource "google_storage_bucket_iam_binding" "public_access" {
  bucket = google_storage_bucket.images.name
  role = "roles/storage.objectViewer"
  members = ["allUsers"]
}

resource "google_storage_bucket_iam_binding" "genmedia_storage_admin" {
  bucket = google_storage_bucket.images.name
  role = "roles/storage.admin"
  members = [
      "serviceAccount:${google_service_account.genmedia_service_account.email}",
    ]
}

# IAM policy for the Cloud Run service
resource "google_cloud_run_v2_service_iam_binding" "genmedia_app_run_invoker" {
  location = google_cloud_run_v2_service.genmedia_app.location
  project  = google_cloud_run_v2_service.genmedia_app.project
  name     = google_cloud_run_v2_service.genmedia_app.name
  role     = "roles/run.invoker"
  members = [
    "serviceAccount:${google_service_account.genmedia_service_invoker_account.email}"
  ]
}

# Grant access to specific secrets
resource "google_secret_manager_secret_iam_member" "some_client_id_access" {
  secret_id = google_secret_manager_secret.some_client_id.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.genmedia_service_account.email}"
  project   = var.project_id
  depends_on = [google_secret_manager_secret.some_client_id]
}