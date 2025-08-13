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

module "storage_account" {
  source  = "Azure/avm-res-storage-storageaccount/azurerm"
  version = "1.0.0"

  name                                 = var.name
  resource_group_name                  = var.resource_group_name
  location                             = var.location
  tags                                 = var.tags
  account_kind                         = var.account_kind
  account_tier                         = var.account_tier
  account_replication_type             = var.account_replication_type
  access_tier                          = var.access_tier
  enable_https_traffic_only            = var.enable_https_traffic_only
  min_tls_version                      = var.min_tls_version
  infrastructure_encryption_enabled    = var.infrastructure_encryption_enabled
  is_hns_enabled                       = var.is_hns_enabled
  nfsv3_enabled                        = var.nfsv3_enabled
  public_network_access_enabled        = var.public_network_access_enabled
  shared_access_key_enabled            = var.shared_access_key_enabled
  allow_nested_items_to_be_public      = var.allow_nested_items_to_be_public
  cross_tenant_replication_enabled     = var.cross_tenant_replication_enabled
  sftp_enabled                         = var.sftp_enabled
  large_file_share_enabled             = var.large_file_share_enabled
  default_to_oauth_authentication      = var.default_to_oauth_authentication
  edge_zone                            = var.edge_zone
  routing                              = var.routing
  lock                                 = var.lock
  managed_identities                   = var.managed_identities
  role_assignments                     = var.role_assignments
  network_rules                        = var.network_rules
  customer_managed_key                 = var.customer_managed_key
  key_vault_access_policy              = var.key_vault_access_policy
  blob_properties                      = var.blob_properties
  containers                           = var.containers
  shares                               = var.shares
  tables                               = var.tables
  queues                               = var.queues
  share_properties                     = var.share_properties
  queue_properties                     = var.queue_properties
  static_website                       = var.static_website
  sas_policy                           = var.sas_policy
  immutability_policy                  = var.immutability_policy
  azure_files_authentication           = var.azure_files_authentication
  private_endpoints                    = var.private_endpoints
  local_user                           = var.local_user
  diagnostic_settings_storage_account  = var.diagnostic_settings_storage_account
  diagnostic_settings_blob             = var.diagnostic_settings_blob
  diagnostic_settings_file             = var.diagnostic_settings_file
  diagnostic_settings_queue            = var.diagnostic_settings_queue
  diagnostic_settings_table            = var.diagnostic_settings_table
  table_encryption_key_type            = var.table_encryption_key_type
  queue_encryption_key_type            = var.queue_encryption_key_type
  enable_telemetry                     = var.enable_telemetry
  timeouts                             = var.timeouts
  # AVM best practice: pass all variables, even if null/default
}