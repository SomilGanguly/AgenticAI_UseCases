terraform {
  required_version = ">= 1.3.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

data "azurerm_client_config" "current" {}

module "keyvault" {
  source  = "Azure/avm-res-keyvault-vault/azurerm"
  version = "1.0.0"

  enable_telemetry                      = var.enable_telemetry
  sku_name                              = var.sku_name
  tenant_id                             = var.tenant_id != "" ? var.tenant_id : data.azurerm_client_config.current.tenant_id
  purge_protection_enabled              = var.purge_protection_enabled
  keys                                  = var.keys
  wait_for_rbac_before_key_operations   = var.wait_for_rbac_before_key_operations
  secrets                               = var.secrets
  enabled_for_template_deployment       = var.enabled_for_template_deployment
  tags                                  = var.tags
  contacts                              = var.contacts
  lock                                  = var.lock
  wait_for_rbac_before_secret_operations = var.wait_for_rbac_before_secret_operations
  resource_group_name                   = var.resource_group_name
  enabled_for_deployment                = var.enabled_for_deployment
  role_assignments                      = var.role_assignments
  private_endpoints                     = var.private_endpoints
  name                                  = var.name
  location                              = var.location
  enabled_for_disk_encryption           = var.enabled_for_disk_encryption
  network_acls                          = var.network_acls
  secrets_value                         = var.secrets_value
}