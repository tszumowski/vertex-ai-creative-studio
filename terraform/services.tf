resource "google_cloud_run_v2_service" "app" {
  name     = "genmedia-app"
  location = var.region
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_ALL"
  template {
    service_account = google_service_account.genmedia_service_account.email
    timeout         = "3600s"
    containers {
      image = data.google_artifact_registry_docker_image.app.self_link
      resources {
        limits = {
          cpu    = "1000m"
          memory = "2Gi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "REGION"
        value = var.region
      }
      env {
        name  = "IMAGE_CREATION_BUCKET"
        value = var.media_bucket
      }
      env {
        name  = "PROJECT_NUMBER"
        value = var.project_number
      }
    }
    scaling {
      min_instance_count = 0
      max_instance_count = 80
    }
  }
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
  depends_on = []
}

