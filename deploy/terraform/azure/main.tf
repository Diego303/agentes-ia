locals {
  suffix = "${var.name}-${var.environment}"
  tags   = merge({ project = "agentes-ia", environment = var.environment, managed_by = "terraform" }, var.tags)

  # Secretos de cada workload: Key Vault → Secret de Kubernetes <workload>-secrets, clave → variable de entorno.
  workload_secrets = {
    "llm-gateway"    = { "anthropic-api-key" = "ANTHROPIC_API_KEY", "litellm-master-key" = "LITELLM_MASTER_KEY", "voyage-api-key" = "VOYAGE_API_KEY" }
    "ops-mcp"        = { "mcp-tokens" = "MCP_TOKENS" }
    "change-advisor" = { "a2a-tokens" = "A2A_TOKENS" }
    "ops-agent"      = { "llm-gateway-key" = "LLM_GATEWAY_KEY", "mcp-token" = "MCP_TOKEN", "advisor-token" = "ADVISOR_TOKEN", "agent-api-tokens" = "AGENT_API_TOKENS" }
  }
  secret_names         = toset(flatten([for secrets in values(local.workload_secrets) : keys(secrets)]))
  sync_service_account = "secrets-sync"
}

data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "this" {
  name     = "rg-${local.suffix}"
  location = var.location
  tags     = local.tags
}

# ------------------------------------------------------------------ registro de imágenes

resource "azurerm_container_registry" "this" {
  name                = "acr${var.name}${var.environment}"
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
  sku                 = "Standard"
  admin_enabled       = false # el clúster tira con su identidad (AcrPull), sin usuario y contraseña
  tags                = local.tags
}

# ------------------------------------------------------------------ clúster

resource "azurerm_kubernetes_cluster" "this" {
  name                = "aks-${local.suffix}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  dns_prefix          = local.suffix
  kubernetes_version  = var.kubernetes_version
  sku_tier            = var.environment == "prod" ? "Standard" : "Free"

  automatic_upgrade_channel = "patch"
  node_os_upgrade_channel   = "NodeImage"
  oidc_issuer_enabled       = true # federación de identidad de los pods con Entra ID
  workload_identity_enabled = true
  local_account_disabled    = true # solo acceso con identidades de Entra ID

  azure_active_directory_role_based_access_control {
    azure_rbac_enabled = true
    tenant_id          = data.azurerm_client_config.current.tenant_id
  }

  default_node_pool {
    name                 = "system"
    vm_size              = var.node_vm_size
    auto_scaling_enabled = true
    min_count            = var.node_count.min
    max_count            = var.node_count.max
    upgrade_settings {
      max_surge = "33%"
    }
  }

  # Pools gestionados explícitamente con cluster autoscaler (Auto = node auto-provisioning).
  node_provisioning_profile {
    mode = "Manual"
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin      = "azure"
    network_plugin_mode = "overlay"
    network_data_plane  = "cilium" # aplica las NetworkPolicy de deploy/kubernetes
    network_policy      = "cilium"
  }

  key_vault_secrets_provider {
    secret_rotation_enabled = true
  }

  tags = local.tags
}

resource "azurerm_role_assignment" "aks_acr_pull" {
  scope                            = azurerm_container_registry.this.id
  role_definition_name             = "AcrPull"
  principal_id                     = azurerm_kubernetes_cluster.this.kubelet_identity[0].object_id
  skip_service_principal_aad_check = true
}

# ------------------------------------------------------------------ secretos

resource "azurerm_key_vault" "this" {
  name                       = "kv-${local.suffix}"
  location                   = azurerm_resource_group.this.location
  resource_group_name        = azurerm_resource_group.this.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  rbac_authorization_enabled = true
  purge_protection_enabled   = true
  soft_delete_retention_days = 7
  tags                       = local.tags
}

# Quien aplica Terraform puede gestionar los valores de los secretos (az keyvault secret set).
resource "azurerm_role_assignment" "operator_secrets" {
  scope                = azurerm_key_vault.this.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = data.azurerm_client_config.current.object_id
}

# Solo se crean los nombres: el valor real se fija fuera de Terraform para que no quede en el state.
resource "azurerm_key_vault_secret" "this" {
  for_each     = local.secret_names
  name         = each.key
  value        = "CAMBIAR"
  key_vault_id = azurerm_key_vault.this.id

  lifecycle {
    ignore_changes = [value]
  }
  depends_on = [azurerm_role_assignment.operator_secrets]
}

# ------------------------------------------------------------------ sincronización de secretos

# Una identidad federada con la ServiceAccount secrets-sync: el pod que monta el Key Vault con el
# driver CSI y sincroniza los valores en los Secrets de Kubernetes que leen los workloads. Los
# workloads no tienen identidad de Azure: solo leen su Secret.
resource "azurerm_user_assigned_identity" "secrets_sync" {
  name                = "id-secrets-sync-${local.suffix}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = local.tags
}

resource "azurerm_federated_identity_credential" "secrets_sync" {
  name                      = "${local.sync_service_account}-${var.namespace}"
  user_assigned_identity_id = azurerm_user_assigned_identity.secrets_sync.id
  audience                  = ["api://AzureADTokenExchange"]
  issuer                    = azurerm_kubernetes_cluster.this.oidc_issuer_url
  subject                   = "system:serviceaccount:${var.namespace}:${local.sync_service_account}"
}

# Lectura solo de los secretos de la aplicación, uno a uno (no de todo el Key Vault).
resource "azurerm_role_assignment" "secrets_sync" {
  for_each             = local.secret_names
  scope                = azurerm_key_vault_secret.this[each.key].resource_versionless_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.secrets_sync.principal_id
}
