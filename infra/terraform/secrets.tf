resource "kubernetes_secret" "auth_secrets" {
  metadata {
    name      = "auth-secrets"
    namespace = kubernetes_namespace.studymate.metadata[0].name
  }

  data = {
    "db-url"     = base64encode(var.auth_db_url)
    "jwt-secret" = base64encode(var.jwt_secret)
  }

  type = "Opaque"
}

resource "kubernetes_secret" "material_secrets" {
  metadata {
    name      = "material-secrets"
    namespace = kubernetes_namespace.studymate.metadata[0].name
  }

  data = {
    "db-url" = base64encode(var.material_db_url)
  }

  type = "Opaque"
}

resource "kubernetes_secret" "memory_secrets" {
  metadata {
    name      = "memory-secrets"
    namespace = kubernetes_namespace.studymate.metadata[0].name
  }

  data = {
    "mongodb-url" = base64encode(var.mongodb_url)
  }

  type = "Opaque"
}