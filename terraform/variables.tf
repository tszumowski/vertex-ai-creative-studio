variable "project_id" {
    type = string
}

variable "region" {
    type = string
    default = "us-central1"
}

variable "media_bucket" {
    type = string
}

variable "backend_bucket_name" {
    type = string
}

variable "test_google_access_token" {
  type    = string
  default = null
}

variable "generation_service_image_tag" {
    type = string
}

variable "api_gateway_image_tag" {
    type = string
}

variable "file_service_image_tag" {
    type = string
}

variable "app_image" {
    type = string
}