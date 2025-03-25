
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


# IAP Policy.
data "google_iam_policy" "iap_users" {
  binding {
    role = "roles/iap.httpsResourceAccessor"
    members = [
        "serviceAccount:${google_service_account.app_sa.email}",
        "allAuthenticatedUsers",
      ]
  }
}

resource "google_iap_web_backend_service_iam_policy" "app" {
  project             = google_compute_backend_service.frontend_backend.project
  web_backend_service = google_compute_backend_service.frontend_backend.name
  policy_data         = data.google_iam_policy.iap_users.policy_data
}