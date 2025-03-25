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

# Service Accounts
resource "google_service_account" "app_sa" {
  account_id   = "genmedia-app-sa"
  display_name = "GenMedia Studio Frontend Service Account"
  project      = var.project_id
}

resource "google_service_account" "iap_sa" {
  account_id   = "genmedia-iap-sa"
  display_name = "GenMedia Studio IAP Service Account"
  project      = var.project_id
}

resource "google_service_account" "generation_service_sa" {
  account_id   = "genmedia-generation-service-sa"
  display_name = "GenMedia Generation Service Service Account"
}

resource "google_service_account" "api_gateway_sa" {
  account_id   = "genmedia-api-gateway-sa"
  display_name = "GenMedia API Gateway Service Account"
}

resource "google_service_account" "file_service_sa" {
  account_id   = "genmedia-file-service-sa"
  display_name = "GenMedia File Service Service Account"
}

resource "google_project_service_identity" "cloudbuild_managed_sa" {
  provider = google-beta
  project  = var.project_id
  service  = "cloudbuild.googleapis.com"
}

resource "google_service_account" "genmedia_service_invoker_account" {
  account_id   = "genmedia-invoker"
  display_name = "GenMedia Invoker Service Account"
}

# Shared SA roles.
resource "google_project_iam_binding" "genmedia_logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"

  members = [
    "serviceAccount:${google_service_account.app_sa.email}",
    "serviceAccount:${google_service_account.api_gateway_sa.email}",
    "serviceAccount:${google_service_account.file_service_sa.email}",
    "serviceAccount:${google_service_account.generation_service_sa.email}",
  ]
}

resource "google_project_iam_binding" "genmedia_logging_viewer" {
  project = var.project_id
  role    = "roles/logging.viewer"

  members = [
    "serviceAccount:${google_service_account.app_sa.email}",
    "serviceAccount:${google_service_account.api_gateway_sa.email}",
    "serviceAccount:${google_service_account.file_service_sa.email}",
    "serviceAccount:${google_service_account.generation_service_sa.email}",
  ]
}

resource "google_project_iam_binding" "genmedia_token_creator" {
  project = var.project_id
  role    = "roles/iam.serviceAccountTokenCreator"

  members = [
    "serviceAccount:${google_service_account.api_gateway_sa.email}",
    "serviceAccount:${google_service_account.file_service_sa.email}",
    "serviceAccount:${google_service_account.generation_service_sa.email}",
  ]
}

resource "google_project_iam_binding" "genmedia_aiplatform_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"

  members = [
    "serviceAccount:${google_service_account.file_service_sa.email}",
    "serviceAccount:${google_service_account.generation_service_sa.email}",
  ]
}

resource "google_project_iam_binding" "genmedia_storage_object_user" {
  project = var.project_id
  role    = "roles/storage.objectUser"

  members = [
    "serviceAccount:${google_service_account.file_service_sa.email}",
    "serviceAccount:${google_service_account.generation_service_sa.email}",
  ]
}

resource "google_project_iam_binding" "genmedia_datastore_user" {
  project = var.project_id
  role    = "roles/datastore.user"

  members = [
    "serviceAccount:${google_service_account.file_service_sa.email}",
    "serviceAccount:${google_service_account.generation_service_sa.email}",
  ]
}

resource "google_project_iam_binding" "genmedia_datastore_viewer" {
  project = var.project_id
  role    = "roles/datastore.viewer"

  members = [
    "serviceAccount:${google_service_account.file_service_sa.email}",
    "serviceAccount:${google_service_account.generation_service_sa.email}",
  ]
}

# Indivdual SA roles.

# Bucket Policy.
resource "google_storage_bucket_iam_binding" "public_access" {
  bucket = google_storage_bucket.images.name
  role = "roles/storage.objectViewer"
  members = ["allUsers"]
}

resource "google_storage_bucket_iam_binding" "genmedia_storage_admin" {
  bucket = google_storage_bucket.images.name
  role = "roles/storage.admin"
  members = [
      "serviceAccount:${google_service_account.file_service_sa.email}",
      "serviceAccount:${google_service_account.generation_service_sa.email}",
    ]
}



# IAM policy for the Cloud Run services
resource "google_cloud_run_v2_service_iam_binding" "genmedia_app_run_invoker" {
  location = google_cloud_run_v2_service.app.location
  project  = google_cloud_run_v2_service.app.project
  name     = google_cloud_run_v2_service.app.name
  role     = "roles/run.invoker"
  members = [
    "serviceAccount:${google_service_account.app_sa.email}",
    "serviceAccount:${google_service_account.iap_sa.email}",
  ]
}

resource "google_cloud_run_v2_service_iam_binding" "genmedia_api_gateway_run_invoker" {
  location = google_cloud_run_v2_service.api_gateway.location
  project  = google_cloud_run_v2_service.api_gateway.project
  name     = google_cloud_run_v2_service.api_gateway.name
  role     = "roles/run.invoker"
  members = [
    "serviceAccount:${google_service_account.app_sa.email}",
    "serviceAccount:${google_service_account.api_gateway_sa.email}",
  ]
}

resource "google_cloud_run_v2_service_iam_binding" "genmedia_generation_service_run_invoker" {
  location = google_cloud_run_v2_service.generation_service.location
  project  = google_cloud_run_v2_service.generation_service.project
  name     = google_cloud_run_v2_service.generation_service.name
  role     = "roles/run.invoker"
  members = [
    "serviceAccount:${google_service_account.api_gateway_sa.email}",
    "serviceAccount:${google_service_account.generation_service_sa.email}",
  ]
}

resource "google_cloud_run_v2_service_iam_binding" "genmedia_file_service_run_invoker" {
  location = google_cloud_run_v2_service.file_service.location
  project  = google_cloud_run_v2_service.file_service.project
  name     = google_cloud_run_v2_service.file_service.name
  role     = "roles/run.invoker"
  members = [
    "serviceAccount:${google_service_account.api_gateway_sa.email}",
    "serviceAccount:${google_service_account.file_service_sa.email}",
  ]
}