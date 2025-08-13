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

module "virtual_network" {
  source  = "Azure/avm-res-network-virtualnetwork/azurerm"
  version = "1.0.0"

  name                                         = var.name
  resource_group_name                          = var.resource_group_name
  vnet_location                                = var.vnet_location
  address_space                                = var.address_space
  address_spaces                               = var.address_spaces
  subnet_names                                 = var.subnet_names
  subnet_prefixes                              = var.subnet_prefixes
  subnet_delegation                            = var.subnet_delegation
  subnet_service_endpoints                     = var.subnet_service_endpoints
  nsg_ids                                      = var.nsg_ids
  route_tables_ids                             = var.route_tables_ids
  private_link_endpoint_network_policies_enabled = var.private_link_endpoint_network_policies_enabled
  private_link_service_network_policies_enabled = var.private_link_service_network_policies_enabled
  ddos_protection_plan                         = var.ddos_protection_plan
  dns_servers                                  = var.dns_servers
  lock                                         = var.lock
  tags                                         = var.tags
  diagnostic_settings                          = var.diagnostic_settings
  private_endpoints                            = var.private_endpoints
  enable_telemetry                             = var.enable_telemetry
  tracing_tags_enabled                         = var.tracing_tags_enabled
  tracing_tags_prefix                          = var.tracing_tags_prefix
  role_assignments                             = var.role_assignments
}