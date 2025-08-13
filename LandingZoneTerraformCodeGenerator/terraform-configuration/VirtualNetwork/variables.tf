variable "name" {
  description = "The name of the virtual network to create."
  type        = string
  default     = "acctvnet"
}

variable "resource_group_name" {
  description = "The name of the resource group where the resources will be deployed."
  type        = string
}

variable "vnet_location" {
  description = "The location/region where the virtual network is created. Changing this forces a new resource to be created."
  type        = string
  default     = null
}

variable "address_space" {
  description = "The address space that is used by the virtual network."
  type        = string
  default     = "10.0.0.0/16"
}

variable "address_spaces" {
  description = "The list of the address spaces that is used by the virtual network."
  type        = list(string)
  default     = []
}

variable "subnet_names" {
  description = "A list of public subnets inside the vNet."
  type        = list(string)
  default     = ["subnet1"]
}

variable "subnet_prefixes" {
  description = "The address prefix to use for the subnet."
  type        = list(string)
  default     = ["10.0.1.0/24"]
}

variable "subnet_delegation" {
  description = "`service_delegation` blocks for `azurerm_subnet` resource, subnet names as keys, list of delegation blocks as value."
  type = map(list(object({
    name = string
    service_delegation = object({
      name    = string
      actions = optional(list(string))
    })
  })))
  default = {}
}

variable "subnet_service_endpoints" {
  description = "A map with key (string) `subnet name`, value (list(string)) to indicate enabled service endpoints on the subnet."
  type        = map(list(string))
  default     = {}
}

variable "nsg_ids" {
  description = "A map of subnet name to Network Security Group IDs."
  type        = map(string)
  default     = {}
}

variable "route_tables_ids" {
  description = "A map of subnet name to Route table ids."
  type        = map(string)
  default     = {}
}

variable "private_link_endpoint_network_policies_enabled" {
  description = "A map with key (string) `subnet name`, value (bool) to enable/disable network policies for the private link endpoint on the subnet."
  type        = map(bool)
  default     = {}
}

variable "private_link_service_network_policies_enabled" {
  description = "A map with key (string) `subnet name`, value (bool) to enable/disable network policies for the private link service on the subnet."
  type        = map(bool)
  default     = {}
}

variable "ddos_protection_plan" {
  description = "The set of DDoS protection plan configuration."
  type = object({
    enable = bool
    id     = string
  })
  default = null
}

variable "dns_servers" {
  description = "The DNS servers to be used with vNet. If no values are specified, this defaults to Azure DNS."
  type        = list(string)
  default     = []
}

variable "lock" {
  description = "The lock level to apply to the Virtual Network. Default is `None`. Possible values are `None`, `CanNotDelete`, and `ReadOnly`."
  type = object({
    name = optional(string, null)
    kind = optional(string, "None")
  })
  default = {}
}

variable "tags" {
  description = "The tags to associate with your network and subnets."
  type        = map(any)
  default     = {}
}

variable "diagnostic_settings" {
  description = "Diagnostic settings for the virtual network."
  type = map(object({
    name                                     = optional(string, null)
    log_categories_and_groups                = optional(set(string), ["allLogs"])
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

variable "private_endpoints" {
  description = "A map of private endpoints to create on the Virtual Network."
  type = map(object({
    role_assignments                        = map(object({}))
    lock                                    = object({})
    tags                                    = optional(map(any), {})
    service                                 = string
    subnet_resource_id                      = string
    private_dns_zone_group_name             = optional(string, null)
    private_dns_zone_resource_ids           = optional(set(string), [])
    application_security_group_resource_ids = optional(set(string), [])
    network_interface_name                  = optional(string, null)
    ip_configurations = optional(map(object({
      name               = string
      group_id           = optional(string, null)
      member_name        = optional(string, null)
      private_ip_address = string
    })), {})
  }))
  default = {}
}

variable "enable_telemetry" {
  description = "This variable controls whether or not telemetry is enabled for the module."
  type        = bool
  default     = true
}

variable "tracing_tags_enabled" {
  description = "Whether enable tracing tags that generated by BridgeCrew Yor."
  type        = bool
  default     = false
}

variable "tracing_tags_prefix" {
  description = "Default prefix for generated tracing tags."
  type        = string
  default     = "avm_"
}

variable "role_assignments" {
  description = "Role assignments to create on the virtual network."
  type = map(object({
    role_definition_id_or_name             = string
    principal_id                           = string
    description                            = optional(string, null)
    skip_service_principal_aad_check       = optional(bool, true)
    condition                              = optional(string, null)
    condition_version                      = optional(string, "2.0")
    delegated_managed_identity_resource_id = optional(string)
  }))
  default = {}
}