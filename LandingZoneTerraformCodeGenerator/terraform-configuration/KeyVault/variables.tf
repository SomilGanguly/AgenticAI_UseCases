variable "enable_telemetry" {
  description = "This variable controls whether or not telemetry is enabled for the module. For more information see https://aka.ms/avm/telemetry. If it is set to false, then no telemetry will be collected."
  type        = bool
  default     = true
}

variable "sku_name" {
  description = "The SKU name of the Key Vault. Possible values are `standard` and `premium`."
  type        = string
  default     = "standard"
  validation {
    condition     = contains(["standard", "premium"], var.sku_name)
    error_message = "sku_name must be either 'standard' or 'premium'."
  }
}

variable "tenant_id" {
  description = "The Azure tenant ID used for authenticating requests to Key Vault. You can use the `azurerm_client_config` data source to retrieve it."
  type        = string
}

variable "purge_protection_enabled" {
  description = "Specifies whether protection against purge is enabled for this Key Vault. Note once enabled this cannot be disabled."
  type        = bool
  default     = true
}

variable "keys" {
  description = "A map of keys to create on the Key Vault. The map key is deliberately arbitrary to avoid issues where many keys may be unknown at plan time."
  type = map(object({
    name     = string
    key_type = string
    key_opts = optional(list(string), ["sign", "verify"])

    key_size        = optional(number, null)
    curve           = optional(string, null)
    not_before_date = optional(string, null)
    expiration_date = optional(string, null)
    tags            = optional(map(any), null)

    role_assignments = optional(map(object({
      role_definition_id_or_name             = string
      principal_id                           = string
      description                            = optional(string, null)
      skip_service_principal_aad_check       = optional(bool, false)
      condition                              = optional(string, null)
      condition_version                      = optional(string, null)
      delegated_managed_identity_resource_id = optional(string, null)
    })), {})

    rotation_policy = optional(object({
      automatic = optional(object({
        time_after_creation = optional(string, null)
        time_before_expiry  = optional(string, null)
      }), null)
      expire_after         = optional(string, null)
      notify_before_expiry = optional(string, null)
    }), null)
  }))
  default = {}
}

variable "wait_for_rbac_before_key_operations" {
  description = "This variable controls the amount of time to wait before performing key operations. It only applies when `var.role_assignments` and `var.keys` are both set. This is useful when you are creating role assignments on the key vault and immediately creating keys in it. The default is 30 seconds for create and 0 seconds for destroy."
  type = object({
    create  = optional(string, "30s")
    destroy = optional(string, "0s")
  })
  default = {}
}

variable "secrets" {
  description = "A map of secrets to create on the Key Vault. The map key is deliberately arbitrary to avoid issues where many keys may be unknown at plan time."
  type = map(object({
    name            = string
    content_type    = optional(string, null)
    tags            = optional(map(any), null)
    not_before_date = optional(string, null)
    expiration_date = optional(string, null)

    role_assignments = optional(map(object({
      role_definition_id_or_name             = string
      principal_id                           = string
      description                            = optional(string, null)
      skip_service_principal_aad_check       = optional(bool, false)
      condition                              = optional(string, null)
      condition_version                      = optional(string, null)
      delegated_managed_identity_resource_id = optional(string, null)
    })), {})
  }))
  default = {}
}

variable "enabled_for_template_deployment" {
  description = "Specifies whether Azure Resource Manager is permitted to retrieve secrets from the vault."
  type        = bool
  default     = false
}

variable "tags" {
  description = "Map of tags to assign to the Key Vault resource."
  type        = map(any)
  default     = null
}

variable "contacts" {
  description = "A map of contacts for the Key Vault. The map key is deliberately arbitrary to avoid issues where many keys may be unknown at plan time."
  type = map(object({
    email = string
    name  = optional(string, null)
    phone = optional(string, null)
  }))
  default = {}
}

variable "lock" {
  description = "The lock level to apply to the Key Vault. Possible values are `None`, `CanNotDelete`, and `ReadOnly`."
  type = object({
    name = optional(string, null)
    kind = optional(string, "None")
  })
  default = {}
  validation {
    condition = (
      var.lock == null ||
      contains(["None", "CanNotDelete", "ReadOnly"], try(var.lock.kind, "None"))
    )
    error_message = "lock.kind must be one of 'None', 'CanNotDelete', or 'ReadOnly'."
  }
}

variable "wait_for_rbac_before_secret_operations" {
  description = "This variable controls the amount of time to wait before performing secret operations. It only applies when `var.role_assignments` and `var.secrets` are both set. This is useful when you are creating role assignments on the key vault and immediately creating secrets in it. The default is 30 seconds for create and 0 seconds for destroy."
  type = object({
    create  = optional(string, "30s")
    destroy = optional(string, "0s")
  })
  default = {}
}

variable "resource_group_name" {
  description = "The resource group where the resources will be deployed."
  type        = string
}

variable "enabled_for_deployment" {
  description = "Specifies whether Azure Virtual Machines are permitted to retrieve certificates stored as secrets from the vault."
  type        = bool
  default     = false
}

variable "role_assignments" {
  description = "A map of role assignments to create on the Key Vault. The map key is deliberately arbitrary to avoid issues where many keys may be unknown at plan time."
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

variable "private_endpoints" {
  description = "A map of private endpoints to create for the Key Vault."
  type = map(object({
    role_assignments = optional(map(object({
      role_definition_id_or_name             = string
      principal_id                           = string
      description                            = optional(string, null)
      skip_service_principal_aad_check       = optional(bool, false)
      condition                              = optional(string, null)
      condition_version                      = optional(string, null)
      delegated_managed_identity_resource_id = optional(string, null)
    })), {})
    lock = object({
      name = optional(string, null)
      kind = optional(string, "None")
    })
    tags                                    = optional(map(any), null)
    service                                 = string
    subnet_resource_id                      = string
    private_dns_zone_group_name             = optional(string, null)
    private_dns_zone_resource_ids           = optional(set(string), [])
    application_security_group_resource_ids = optional(set(string), [])
    private_service_connection_name         = optional(string, null)
    network_interface_name                  = optional(string, null)
    location                                = optional(string, null)
    resource_group_name                     = optional(string, null)
    ip_configurations = optional(map(object({
      name               = string
      subresource_name   = optional(string, "vault")
      member_name        = optional(string, "vault")
      private_ip_address = string
    })), {})
  }))
  default = {}
}

variable "name" {
  description = "The name of the Key Vault."
  type        = string
}

variable "location" {
  description = "The Azure location where the resources will be deployed."
  type        = string
}

variable "enabled_for_disk_encryption" {
  description = "Specifies whether Azure Disk Encryption is permitted to retrieve secrets from the vault and unwrap keys."
  type        = bool
  default     = false
}

variable "network_acls" {
  description = "Network ACLs for the Key Vault."
  type = object({
    bypass                     = optional(string, "None")
    default_action             = optional(string, "Deny")
    ip_rules                   = optional(list(string), [])
    virtual_network_subnet_ids = optional(list(string), [])
  })
  default = null
}

variable "secrets_value" {
  description = "A map of secret keys to values. The map key is the supplied input to var.secrets. The map value is the secret value."
  type        = map(string)
  default     = {}
  sensitive   = true
}