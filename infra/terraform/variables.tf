variable "auth_db_url" {
  description = "PostgreSQL URL for Auth Service"
  type        = string
  sensitive   = true
  default     = "postgresql://auth_user:auth_pass@postgres-auth:5432/auth_db"
}

variable "material_db_url" {
  description = "PostgreSQL URL for Material Service"
  type        = string
  sensitive   = true
  default     = "postgresql://material_user:material_pass@postgres-material:5432/material_db"
}

variable "mongodb_url" {
  description = "MongoDB URL for Memory Service"
  type        = string
  sensitive   = true
  default     = "mongodb://mongo_user:mongo_pass@mongodb:27017/memory_db?authSource=admin"
}

variable "jwt_secret" {
  description = "JWT Secret Key"
  type        = string
  sensitive   = true
  default     = "supersecretjwtkey123"
}

variable "namespace" {
  description = "Kubernetes namespace"
  type        = string
  default     = "studymate"
}

variable "image_tag" {
  description = "Docker image tag"
  type        = string
  default     = "latest"
}