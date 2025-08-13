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

data "azurerm_resource_group" "this" {
  name = var.resource_group_name
}

module "network_security_group" {
  source  = "Azure/avm-res-network-networksecuritygroup/azurerm"
  version = "1.0.0"

  name                = var.name
  location            = var.location
  resource_group_name = data.azurerm_resource_group.this.name
  # nsgrules            = var.nsgrules
  tags                = var.tags
  enable_telemetry    = var.enable_telemetry
  role_assignments    = var.role_assignments
  lock                = var.lock
  diagnostic_settings = var.diagnostic_settings
}