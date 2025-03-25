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

resource "google_storage_bucket" "images" {
  name          = var.media_bucket
  location      = var.region
  project       = var.project_id

  uniform_bucket_level_access = true
  public_access_prevention = "inherited"
}

resource "google_firestore_database" "database" {
  project                           = var.project_id
  name                              = "genmedia-studio"
  location_id                       = "nam5"
  type                              = "FIRESTORE_NATIVE"
  concurrency_mode                  = "OPTIMISTIC"
  app_engine_integration_mode       = "DISABLED"
  point_in_time_recovery_enablement = "POINT_IN_TIME_RECOVERY_ENABLED"
  delete_protection_state           = "DELETE_PROTECTION_ENABLED"
  deletion_policy                   = "DELETE"
}

resource "google_firestore_index" "vector-index" {
  project     = var.project_id
  database   = google_firestore_database.database.name
  collection = "image-metadata"

  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }

  fields {
    field_path = "image_embeddings"
    vector_config {
      dimension = 256
      flat {}
    }
  }
}

resource "google_firestore_index" "timestamp-index" {
  project     = var.project_id
  database   = google_firestore_database.database.name
  collection = "image-metadata"

  fields {
    field_path = "timestamp"
    order      = "DESCENDING"
  }

  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}