output "resource_group" {
  value = azurerm_resource_group.this.name
}

output "aks_name" {
  value = azurerm_kubernetes_cluster.this.name
}

output "acr_login_server" {
  value = azurerm_container_registry.this.login_server
}

output "key_vault_name" {
  value = azurerm_key_vault.this.name
}

output "tenant_id" {
  value = data.azurerm_client_config.current.tenant_id
}

output "secrets_sync_client_id" {
  value = azurerm_user_assigned_identity.secrets_sync.client_id
}

output "kubernetes_azure" {
  description = "Manifiestos propios de Azure (Key Vault, sincronización de secretos y ConfigMap del entorno): terraform output -raw kubernetes_azure | kubectl apply -f -"
  value = templatefile("${path.module}/templates/kubernetes-azure.yaml.tftpl", {
    namespace           = var.namespace
    service_account     = local.sync_service_account
    client_id           = azurerm_user_assigned_identity.secrets_sync.client_id
    tenant_id           = data.azurerm_client_config.current.tenant_id
    key_vault           = azurerm_key_vault.this.name
    workload_secrets    = local.workload_secrets
    otel_traces_backend = var.otel_traces_backend
    mcp_issuer_url      = coalesce(var.mcp_issuer_url, "https://login.microsoftonline.com/${data.azurerm_client_config.current.tenant_id}/v2.0")
  })
}
