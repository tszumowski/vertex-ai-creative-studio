resource "google_storage_bucket" "images" {
  name          = format("%s-%s", var.project_id, "images")
  location      = var.region
  project       = var.project_id

  uniform_bucket_level_access = true
  public_access_prevention = "inherited"
}
