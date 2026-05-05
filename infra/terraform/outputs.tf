output "namespace" {
  description = "Kubernetes namespace"
  value       = kubernetes_namespace.studymate.metadata[0].name
}

output "auth_service_account" {
  description = "Auth service account name"
  value       = kubernetes_service_account.auth_service.metadata[0].name
}

output "ai_service_account" {
  description = "AI service account name"
  value       = kubernetes_service_account.ai_service.metadata[0].name
}