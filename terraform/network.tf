resource "google_compute_global_address" "default" {
  name          = "global-genmedia-studio-default"
  address_type  = "EXTERNAL"

  # Create a network only if the compute.googleapis.com API has been activated.
  depends_on = [google_project_service.apis]
  project = var.project_id
}

resource "google_compute_region_network_endpoint_group" "frontend_neg" {
  name                  = "genmedia-studio-frontend-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  project               = var.project_id
  cloud_run {
    service = google_cloud_run_v2_service.app.name
  }
  lifecycle {
   create_before_destroy = true
 }
}

resource "google_compute_backend_service" "frontend_backend" {
  name                            = "genmedia-studio-frontend-backend-service"
  enable_cdn                      = false
  connection_draining_timeout_sec = 10
  project                         = var.project_id

  backend {
    group = google_compute_region_network_endpoint_group.frontend_neg.id
  }

  iap {
    enabled              = true
    oauth2_client_id = google_iap_client.default.client_id
    oauth2_client_secret = google_iap_client.default.secret
  }

  load_balancing_scheme = "EXTERNAL"
  protocol              = "HTTP"
}

resource "google_compute_url_map" "default" {
  name             = "genmedia-studio-http-lb"
  default_service  = google_compute_backend_service.frontend_backend.id
  project          = var.project_id

  host_rule {
    hosts        = ["*"]
    path_matcher = "allpaths"
  }

  path_matcher {
    name = "allpaths"
    default_service = google_compute_backend_service.frontend_backend.id
  }
}

resource "google_compute_target_https_proxy" "default" {
  name    = "genmedia-studio-default-https-lb-proxy"
  url_map = google_compute_url_map.default.id
  project = var.project_id
  ssl_certificates = [
    google_compute_managed_ssl_certificate.default.id,
  ]
}

resource "google_compute_global_forwarding_rule" "default" {
  name = "genmedia-studio-default-https-lb-forwarding-rule"
  project = var.project_id
  ip_protocol = "TCP"
  load_balancing_scheme = "EXTERNAL"
  port_range = "443"
  target = google_compute_target_https_proxy.default.id
  ip_address = google_compute_global_address.default.id
}