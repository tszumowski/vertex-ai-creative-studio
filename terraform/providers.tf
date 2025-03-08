terraform {
  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "3.4.3"
    }
    google = {
      source  = "hashicorp/google"
      version = "6.14.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "6.14.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.0.2"
    }
  }
}


provider "google" {
  access_token = var.test_google_access_token
  project      = var.project_id
  region       = var.region
}

provider "google-beta" {
  access_token = var.test_google_access_token
  project      = var.project_id
  region       = var.region
}

data "google_client_config" "default" {}

provider "docker" {
  registry_auth {
    address  = "gcr.io"
    username = "oauth2accesstoken"
    password = data.google_client_config.default.access_token
  }
}