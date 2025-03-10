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