variable "project_id" {
  type = string
  description = "Your Google Cloud project ID"
}

variable "region" {
  type = string
  description = "Region where the worloads run"
}

variable "service_name" {
  type = string
  description = "Your Cloud Run service name"
}

variable "firestore_database" {
  type = string
  description = "Firestore database name"
}
