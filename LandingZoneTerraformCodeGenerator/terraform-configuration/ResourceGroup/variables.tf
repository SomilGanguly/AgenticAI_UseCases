variable "location" {
  description = "Required. The Azure region for deployment of the this resource."
  type        = string

  validation {
    condition     = length(var.location) > 0
    error_message = "The location must not be empty."
  }
}

variable "name" {
  description = "Required. The name of the this resource."
  type        = string

  validation {
    condition     = length(var.name) > 0
    error_message = "The resource group name must not be empty."
  }
}

variable "enable_telemetry" {
  description = "This variable controls whether or not telemetry is enabled for the module. For more information see https://aka.ms/avm/telemetryinfo. If it is set to false, then no telemetry will be collected."
  type        = bool
  default     = true
}

variable "lock" {
  description = "Controls the Resource Lock configuration for this resource. The following properties can be specified:\n- kind (Required): The type of lock. Possible values are \"CanNotDelete\" and \"ReadOnly\".\n- name (Optional): The name of the lock. If not specified, a name will be generated based on the kind value. Changing this forces the creation of a new resource."
  type = object({
    kind = string
    name = optional(string, null)
  })
  default = null

  validation {
    condition = var.lock == null ? true : contains(["CanNotDelete", "ReadOnly"], var.lock.kind)
    error_message = "If specified, lock.kind must be either 'CanNotDelete' or 'ReadOnly'."
  }
}

variable "role_assignments" {
  description = "Optional. A map of role assignments to create on this resource. The map key is deliberately arbitrary to avoid issues where map keys maybe unknown at plan time."
  type = map(object({
    role_definition_id_or_name             = string
    principal_id                           = string
    description                            = optional(string, null)
    skip_service_principal_aad_check       = optional(bool, false)
    condition                              = optional(string, null)
    condition_version                      = optional(string, null)
    delegated_managed_identity_resource_id = optional(string, null)
    principal_type                         = optional(string, null)
  }))
  default = {}
}

variable "tags" {
  description = "(Optional) Tags of the resource."
  type        = map(string)
  default     = null
}