resource "helm_release" "studymate_ai" {
  name       = "studymate-ai"
  chart      = "../../infra/helm/studymate-ai"
  namespace  = kubernetes_namespace.studymate.metadata[0].name

  values = [
    file("../../infra/helm/studymate-ai/values.yaml")
  ]

  set {
    name  = "global.imageTag"
    value = var.image_tag
  }

  depends_on = [
    kubernetes_namespace.studymate,
    kubernetes_secret.auth_secrets,
    kubernetes_secret.material_secrets,
    kubernetes_secret.memory_secrets
  ]
}