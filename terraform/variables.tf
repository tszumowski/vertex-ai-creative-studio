variable "project_id" {
    type = string
}

variable "project_number" {
    type = string
}

variable "region" {
    type = string
    default = "us-central1"
}

variable "media_bucket" {
    type = string
}

variable "test_google_access_token" {
  type    = string
  default = null
}

variable "db_name" {
    type  = string
}

variable "iap_brand_id" {
  description = "Existing IAP Brand ID - only INTERNAL TYPE (you can obtain it using this command: `$ gcloud iap oauth-brands list --format='value(name)' | sed 's:.*/::'`)."
}