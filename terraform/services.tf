resource "google_cloud_run_v2_service" "app" {
  name     = "genmedia-app"
  location = var.region
  deletion_protection = false
  ingress = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }
    service_account = google_service_account.app_sa.email
    containers {
      image = data.google_artifact_registry_docker_image.app.self_link
      resources {
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
  }
}

resource "google_cloud_run_v2_service" "api_gateway" {
  name     = "genmedia-api-gateway"
  location = var.region
  deletion_protection = false
  ingress = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }
    service_account = google_service_account.api_gateway_sa.email
    containers {
      ports {
        container_port = 8000
      }
      image = data.google_artifact_registry_docker_image.api_gateway.self_link
      resources {
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
  }
}

resource "google_cloud_run_v2_service" "file_service" {
  name     = "genmedia-file-service"
  location = var.region
  deletion_protection = false
  ingress = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }
    service_account = google_service_account.file_service_sa.email
    containers {
      ports {
        container_port = 8000
      }
      image = data.google_artifact_registry_docker_image.file_service.self_link
      resources {
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
      env {
        name  = "DB_NAME"
        value = var.db_name
      }
    }
  }
}

resource "google_cloud_run_v2_service" "generation_service" {
  name     = "genmedia-generation-service"
  location = var.region
  deletion_protection = false
  ingress = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }
    service_account = google_service_account.generation_service_sa.email
    containers {
      ports {
        container_port = 8000
      }
      image = data.google_artifact_registry_docker_image.generation_service.self_link
      resources {
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
      env {
        name  = "DB_NAME"
        value = var.db_name
      }
    }
  }
}



