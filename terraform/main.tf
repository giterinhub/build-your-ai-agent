terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "~> 4.52"
    }
    google-beta = {
      source = "hashicorp/google-beta"
      version = "~> 5.30"
    }    
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = ["allUsers"]
  }
}

# Artifact Registry Repository
resource "google_artifact_registry_repository" "repository" {
  provider      = google-beta
  location      = var.region
  repository_id = var.service_name
  format        = "DOCKER"
}

# Cloud Run Service
resource "google_cloud_run_v2_service" "demo_service" {
  name     = var.service_name
  location = var.region
  ingress = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
        image = "us-docker.pkg.dev/cloudrun/container/hello"
        env {
            name  = "PROJECT_ID"
            value = var.project_id
        }
        env {
            name  = "REGION"
            value = var.region
        }   
        env {
            name  = "FIRESTORE_DATABASE"
            value = var.firestore_database
        }
    }
    service_account = google_service_account.service_account.email
  }
}


# Service Account for Cloud Run
resource "google_service_account" "service_account" {
  account_id   = "${var.service_name}-sa"
}

# Permissions
resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.service_account.email}"
}

resource "google_project_iam_member" "firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.service_account.email}"
}

resource "google_cloud_run_service_iam_policy" "noauth" {
   location    = google_cloud_run_v2_service.demo_service.location
   project     = google_cloud_run_v2_service.demo_service.project
   service     = google_cloud_run_v2_service.demo_service.name

   policy_data = data.google_iam_policy.noauth.policy_data
}