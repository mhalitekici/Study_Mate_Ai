terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }
  required_version = ">= 1.5.0"
}

provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = "docker-desktop"
}

provider "helm" {
  kubernetes {
    config_path    = "~/.kube/config"
    config_context = "docker-desktop"
  }
}

# Namespace
resource "kubernetes_namespace" "studymate" {
  metadata {
    name = "studymate"
    labels = {
      "istio-injection" = "enabled"
      "managed-by"      = "terraform"
    }
  }
}

# Service Accounts
resource "kubernetes_service_account" "auth_service" {
  metadata {
    name      = "auth-service-sa"
    namespace = kubernetes_namespace.studymate.metadata[0].name
  }
}

resource "kubernetes_service_account" "ai_service" {
  metadata {
    name      = "ai-service-sa"
    namespace = kubernetes_namespace.studymate.metadata[0].name
  }
}

resource "kubernetes_service_account" "multi_agent" {
  metadata {
    name      = "multi-agent-sa"
    namespace = kubernetes_namespace.studymate.metadata[0].name
  }
}