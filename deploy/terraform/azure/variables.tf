variable "subscription_id" {
  description = "Suscripción de Azure donde se despliega."
  type        = string
}

variable "name" {
  description = "Prefijo de los recursos (minúsculas y dígitos)."
  type        = string
  default     = "opsagent"
  validation {
    condition     = can(regex("^[a-z0-9]{3,12}$", var.name))
    error_message = "Entre 3 y 12 caracteres en minúsculas o dígitos (lo exigen los nombres de ACR y Key Vault)."
  }
}

variable "environment" {
  type    = string
  default = "dev"
  validation {
    condition     = contains(["dev", "pre", "prod"], var.environment)
    error_message = "environment debe ser dev, pre o prod."
  }
}

variable "location" {
  type    = string
  default = "westeurope"
}

variable "kubernetes_version" {
  description = "Versión de AKS; null usa la versión por defecto de la región."
  type        = string
  default     = null
}

variable "node_vm_size" {
  type    = string
  default = "Standard_D4ds_v5"
}

variable "node_count" {
  description = "Mínimo y máximo del autoescalado del pool de nodos."
  type        = object({ min = number, max = number })
  default     = { min = 2, max = 5 }
}

variable "namespace" {
  description = "Namespace de Kubernetes de los workloads (sujeto de la federación de identidad)."
  type        = string
  default     = "opsagent"
}

variable "tags" {
  type    = map(string)
  default = {}
}

variable "otel_traces_backend" {
  description = "Endpoint OTLP/HTTP del backend de trazas (Grafana Tempo, Honeycomb, Azure Monitor...)."
  type        = string
}

variable "mcp_issuer_url" {
  description = "Emisor de los tokens del servidor MCP; null usa Entra ID del tenant."
  type        = string
  default     = null
}
