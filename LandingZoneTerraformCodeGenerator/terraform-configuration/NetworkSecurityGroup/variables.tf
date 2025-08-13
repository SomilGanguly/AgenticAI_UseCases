variable "enable_telemetry" {
  description = "This variable controls whether or not telemetry is enabled for the module. For more information see https://aka.ms/avm/telemetryinfo. If it is set to false, then no telemetry will be collected."
  type        = bool
  default     = true
}

variable "role_assignments" {
  description = "A map of role assignments to create on this resource. The map key is deliberately arbitrary to avoid issues where map keys maybe unknown at plan time."
  type = map(object({
    role_definition_id_or_name             = string
    principal_id                           = string
    description                            = optional(string, null)
    skip_service_principal_aad_check       = optional(bool, false)
    condition                              = optional(string, null)
    condition_version                      = optional(string, null)
    delegated_managed_identity_resource_id = optional(string, null)
  }))
  default = {}
}

variable "location" {
  description = "The Azure location where the resources will be deployed."
  type        = string
}

variable "nsgrules" {
  description = "NSG rules to create"
  type = map(object({
    nsg_rule_priority                   = number
    nsg_rule_direction                  = string
    nsg_rule_access                     = string
    nsg_rule_protocol                   = string
    nsg_rule_source_port_range          = string
    nsg_rule_destination_port_range     = string
    nsg_rule_source_address_prefix      = string
    nsg_rule_destination_address_prefix = string
  }))
}

variable "tags" {
  description = "Map of tags to assign to the deployed resource."
  type        = map(any)
  default     = null
}

variable "lock" {
  description = "The lock level to apply to the deployed resource. Default is `None`. Possible values are `None`, `CanNotDelete`, and `ReadOnly`."
  type = object({
    name = optional(string, null)
    kind = optional(string, "None")
  })
  default = {}
}

variable "diagnostic_settings" {
  description = "A map of diagnostic settings to create on the ddos protection plan. The map key is deliberately arbitrary to avoid issues where map keys maybe unknown at plan time."
  type = map(object({
    name                                     = optional(string, null)
    log_categories                           = optional(set(string), [])
    log_groups                               = optional(set(string), ["allLogs"])
    metric_categories                        = optional(set(string), ["AllMetrics"])
    log_analytics_destination_type           = optional(string, "Dedicated")
    workspace_resource_id                    = optional(string, null)
    storage_account_resource_id              = optional(string, null)
    event_hub_authorization_rule_resource_id = optional(string, null)
    event_hub_name                           = optional(string, null)
    marketplace_partner_resource_id          = optional(string, null)
  }))
  default = {}
}

variable "resource_group_name" {
  description = "The resource group where the resources will be deployed."
  type        = string
}

variable "name" {
  description = "Name of Network Security Group resource"
  type        = string
}