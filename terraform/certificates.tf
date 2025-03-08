locals {
  secured_domain = "genmediastudio.${google_compute_global_address.default.address}.nip.io"
}

resource "google_compute_managed_ssl_certificate" "default" {
  name = "genmedia-studio-managed"
  project = var.project_id

  managed {
    domains = [local.secured_domain]
  }
}