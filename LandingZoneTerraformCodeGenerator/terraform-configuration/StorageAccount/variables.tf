variable "name" {
  description = "The name of the resource."
  type        = string
}

variable "resource_group_name" {
  description = "The resource group where the resources will be deployed."
  type        = string
}

variable "location" {
  description = "Azure region where the resource should be deployed. If null, the location will be inferred from the resource group location."
  type        = string
  default     = null
}

variable "tags" {
  description = "Custom tags to apply to the resource."
  type        = map(string)
  default     = {}
}

variable "account_kind" {
  description = "(Optional) Defines the Kind of account. Valid options are `BlobStorage`, `BlockBlobStorage`, `FileStorage`, `Storage` and `StorageV2`. Defaults to `StorageV2`."
  type        = string
  default     = "StorageV2"
  validation {
    condition     = contains(["BlobStorage", "BlockBlobStorage", "FileStorage", "Storage", "StorageV2"], var.account_kind)
    error_message = "account_kind must be one of BlobStorage, BlockBlobStorage, FileStorage, Storage, StorageV2."
  }
}

variable "account_tier" {
  description = "(Required) Defines the Tier to use for this storage account. Valid options are `Standard` and `Premium`."
  type        = string
  default     = "Standard"
  validation {
    condition     = contains(["Standard", "Premium"], var.account_tier)
    error_message = "account_tier must be Standard or Premium."
  }
}

variable "account_replication_type" {
  description = "(Required) Defines the type of replication to use for this storage account. Valid options are `LRS`, `GRS`, `RAGRS`, `ZRS`, `GZRS` and `RAGZRS`.  Defaults to `RAGZRS`"
  type        = string
  default     = "RAGZRS"
  validation {
    condition     = contains(["LRS", "GRS", "RAGRS", "ZRS", "GZRS", "RAGZRS"], var.account_replication_type)
    error_message = "account_replication_type must be one of LRS, GRS, RAGRS, ZRS, GZRS, RAGZRS."
  }
}

variable "access_tier" {
  description = "(Optional) Defines the access tier for `BlobStorage`, `FileStorage` and `StorageV2` accounts. Valid options are `Hot` and `Cool`, defaults to `Hot`."
  type        = string
  default     = "Hot"
  validation {
    condition     = contains(["Hot", "Cool"], var.access_tier)
    error_message = "access_tier must be Hot or Cool."
  }
}

variable "enable_https_traffic_only" {
  description = "(Optional) Boolean flag which forces HTTPS if enabled. Defaults to `true`."
  type        = bool
  default     = true
}

variable "min_tls_version" {
  description = "(Optional) The minimum supported TLS version for the storage account. Possible values are `TLS1_0`, `TLS1_1`, and `TLS1_2`. Defaults to `TLS1_2`."
  type        = string
  default     = "TLS1_2"
  validation {
    condition     = contains(["TLS1_0", "TLS1_1", "TLS1_2"], var.min_tls_version)
    error_message = "min_tls_version must be one of TLS1_0, TLS1_1, TLS1_2."
  }
}

variable "infrastructure_encryption_enabled" {
  description = "(Optional) Is infrastructure encryption enabled? Changing this forces a new resource to be created. Defaults to `false`."
  type        = bool
  default     = false
}

variable "is_hns_enabled" {
  description = "(Optional) Is Hierarchical Namespace enabled? This can be used with Azure Data Lake Storage Gen 2."
  type        = bool
  default     = null
}

variable "nfsv3_enabled" {
  description = "(Optional) Is NFSv3 protocol enabled? Changing this forces a new resource to be created. Defaults to `false`."
  type        = bool
  default     = false
}

variable "public_network_access_enabled" {
  description = "(Optional) Whether the public network access is enabled? Defaults to `false`."
  type        = bool
  default     = false
}

variable "shared_access_key_enabled" {
  description = "(Optional) Indicates whether the storage account permits requests to be authorized with the account access key via Shared Key. Defaults to `false`."
  type        = bool
  default     = false
}

variable "allow_nested_items_to_be_public" {
  description = "(Optional) Allow or disallow nested items within this Account to opt into being public. Defaults to `false`."
  type        = bool
  default     = false
}

variable "cross_tenant_replication_enabled" {
  description = "(Optional) Should cross Tenant replication be enabled? Defaults to `false`."
  type        = bool
  default     = false
}

variable "sftp_enabled" {
  description = "(Optional) Boolean, enable SFTP for the storage account.  Defaults to `false`."
  type        = bool
  default     = false
}

variable "large_file_share_enabled" {
  description = "(Optional) Is Large File Share Enabled?"
  type        = bool
  default     = null
}

variable "default_to_oauth_authentication" {
  description = "(Optional) Default to Azure Active Directory authorization in the Azure portal when accessing the Storage Account. The default value is `false`."
  type        = bool
  default     = null
}

variable "edge_zone" {
  description = "(Optional) Specifies the Edge Zone within the Azure Region where this Storage Account should exist."
  type        = string
  default     = null
}

variable "routing" {
  description = "Specifies the kind of network routing opted by the user."
  type = object({
    choice                      = optional(string, "MicrosoftRouting")
    publish_internet_endpoints  = optional(bool, false)
    publish_microsoft_endpoints = optional(bool, false)
  })
  default = null
}

variable "lock" {
  description = "The lock level to apply. Default is `None`. Possible values are `None`, `CanNotDelete`, and `ReadOnly`."
  type = object({
    name = optional(string, null)
    kind = optional(string, "None")
  })
  default = {}
}

variable "managed_identities" {
  description = "Controls the Managed Identity configuration on this resource."
  type = object({
    system_assigned            = optional(bool, false)
    user_assigned_resource_ids = optional(set(string), [])
  })
  default = {}
}

variable "role_assignments" {
  description = "A map of role assignments to create on the resource."
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

variable "network_rules" {
  description = "Network rules for the storage account."
  type = object({
    bypass                     = optional(set(string), [])
    default_action             = optional(string, "Deny")
    ip_rules                   = optional(set(string), [])
    virtual_network_subnet_ids = optional(set(string), [])
    private_link_access = optional(list(object({
      endpoint_resource_id = string
      endpoint_tenant_id   = optional(string)
    })))
    timeouts = optional(object({
      create = optional(string)
      delete = optional(string)
      read   = optional(string)
      update = optional(string)
    }))
  })
  default = {}
}

variable "customer_managed_key" {
  description = "Defines a customer managed key to use for encryption."
  type = object({
    key_vault_resource_id              = string
    key_name                           = string
    key_version                        = optional(string, null)
    user_assigned_identity_resource_id = string
  })
  default = null
}

variable "key_vault_access_policy" {
  description = "Since storage account's customer managed key might require key vault permission, you can create the corresponding permission by setting this variable."
  type = map(object({
    key_permissions = optional(list(string), [
      "Get",
      "UnwrapKey",
      "WrapKey"
    ])
    identity_principle_id = string
    identity_tenant_id    = string
    timeouts = optional(object({
      create = optional(string)
      delete = optional(string)
      read   = optional(string)
      update = optional(string)
    }))
  }))
  default = {}
}

variable "blob_properties" {
  description = "Blob service properties for the storage account."
  type = object({
    change_feed_enabled           = optional(bool)
    change_feed_retention_in_days = optional(number)
    default_service_version       = optional(string)
    last_access_time_enabled      = optional(bool)
    versioning_enabled            = optional(bool)
    container_delete_retention_policy = optional(object({
      days = optional(number)
    }))
    cors_rule = optional(list(object({
      allowed_headers    = list(string)
      allowed_methods    = list(string)
      allowed_origins    = list(string)
      exposed_headers    = list(string)
      max_age_in_seconds = number
    })))
    delete_retention_policy = optional(object({
      days = optional(number)
    }))
    diagnostic_settings = optional(map(object({
      name                                     = optional(string, null)
      log_categories                           = optional(set(string), [])
      log_groups                               = optional(set(string), ["allLogs"])
      metric_categories                        = optional(set(string), ["AllMetrics"])
      log_analytics_destination_type           = optional(string, "Dedicated")
      workspace_resource_id                    = optional(string, null)
      resource_id                              = optional(string, null)
      event_hub_authorization_rule_resource_id = optional(string, null)
      event_hub_name                           = optional(string, null)
      marketplace_partner_resource_id          = optional(string, null)
    })), {})
    restore_policy = optional(object({
      days = number
    }))
  })
  default = null
}

variable "containers" {
  description = "A map of storage containers to create."
  type = map(object({
    public_access = optional(string, "None")
    metadata      = optional(map(string))
    name          = string
    role_assignments = optional(map(object({
      role_definition_id_or_name             = string
      principal_id                           = string
      description                            = optional(string, null)
      skip_service_principal_aad_check       = optional(bool, false)
      condition                              = optional(string, null)
      condition_version                      = optional(string, null)
      delegated_managed_identity_resource_id = optional(string, null)
    })), {})
    timeouts = optional(object({
      create = optional(string)
      delete = optional(string)
      read   = optional(string)
      update = optional(string)
    }))
  }))
  default = {}
}

variable "shares" {
  description = "A map of file shares to create."
  type = map(object({
    access_tier      = optional(string)
    enabled_protocol = optional(string)
    metadata         = optional(map(string))
    name             = string
    quota            = number
    acl = optional(set(object({
      id = string
      access_policy = optional(list(object({
        expiry      = optional(string)
        permissions = string
        start       = optional(string)
      })))
    })))
    timeouts = optional(object({
      create = optional(string)
      delete = optional(string)
      read   = optional(string)
      update = optional(string)
    }))
  }))
  default = {}
}

variable "tables" {
  description = "A map of storage tables to create."
  type = map(object({
    name = string
    acl = optional(set(object({
      id = string
      access_policy = optional(list(object({
        expiry      = string
        permissions = string
        start       = string
      })))
    })))
    timeouts = optional(object({
      create = optional(string)
      delete = optional(string)
      read   = optional(string)
      update = optional(string)
    }))
  }))
  default = {}
}

variable "queues" {
  description = "A map of storage queues to create."
  type = map(object({
    metadata = optional(map(string))
    name     = string
    timeouts = optional(object({
      create = optional(string)
      delete = optional(string)
      read   = optional(string)
      update = optional(string)
    }))
  }))
  default = {}
}

variable "share_properties" {
  description = "Share properties for the storage account."
  type = object({
    cors_rule = optional(list(object({
      allowed_headers    = list(string)
      allowed_methods    = list(string)
      allowed_origins    = list(string)
      exposed_headers    = list(string)
      max_age_in_seconds = number
    })))
    diagnostic_settings = optional(map(object({
      name                                     = optional(string, null)
      log_categories                           = optional(set(string), [])
      log_groups                               = optional(set(string), ["allLogs"])
      metric_categories                        = optional(set(string), ["AllMetrics"])
      log_analytics_destination_type           = optional(string, "Dedicated")
      workspace_resource_id                    = optional(string, null)
      resource_id                              = optional(string, null)
      event_hub_authorization_rule_resource_id = optional(string, null)
      event_hub_name                           = optional(string, null)
      marketplace_partner_resource_id          = optional(string, null)
    })), {})
    retention_policy = optional(object({
      days = optional(number)
    }))
    smb = optional(object({
      authentication_types            = optional(set(string))
      channel_encryption_type         = optional(set(string))
      kerberos_ticket_encryption_type = optional(set(string))
      multichannel_enabled            = optional(bool)
      versions                        = optional(set(string))
    }))
  })
  default = null
}

variable "queue_properties" {
  description = "Queue properties for the storage account."
  type = object({
    cors_rule = optional(list(object({
      allowed_headers    = list(string)
      allowed_methods    = list(string)
      allowed_origins    = list(string)
      exposed_headers    = list(string)
      max_age_in_seconds = number
    })))
    diagnostic_settings = optional(map(object({
      name                                     = optional(string, null)
      log_categories                           = optional(set(string), [])
      log_groups                               = optional(set(string), ["allLogs"])
      metric_categories                        = optional(set(string), ["AllMetrics"])
      log_analytics_destination_type           = optional(string, "Dedicated")
      workspace_resource_id                    = optional(string, null)
      resource_id                              = optional(string, null)
      event_hub_authorization_rule_resource_id = optional(string, null)
      event_hub_name                           = optional(string, null)
      marketplace_partner_resource_id          = optional(string, null)
    })), {})
    hour_metrics = optional(object({
      enabled               = bool
      include_apis          = optional(bool)
      retention_policy_days = optional(number)
      version               = string
    }))
    logging = optional(object({
      delete                = bool
      read                  = bool
      retention_policy_days = optional(number)
      version               = string
      write                 = bool
    }))
    minute_metrics = optional(object({
      enabled               = bool
      include_apis          = optional(bool)
      retention_policy_days = optional(number)
      version               = string
    }))
  })
  default = null
}

variable "static_website" {
  description = "Static website configuration for the storage account."
  type = object({
    error_404_document = optional(string)
    index_document     = optional(string)
  })
  default = null
}

variable "sas_policy" {
  description = "SAS policy for the storage account."
  type = object({
    expiration_action = optional(string, "Log")
    expiration_period = string
  })
  default = null
}

variable "immutability_policy" {
  description = "Immutability policy for the storage account."
  type = object({
    allow_protected_append_writes = bool
    period_since_creation_in_days = number
    state                        = string
  })
  default = null
}

variable "azure_files_authentication" {
  description = "Azure Files authentication configuration."
  type = object({
    directory_type = string
    active_directory = optional(object({
      domain_guid         = string
      domain_name         = string
      domain_sid          = string
      forest_name         = string
      netbios_domain_name = string
      storage_sid         = string
    }))
  })
  default = null
}

variable "private_endpoints" {
  description = "A map of private endpoints to create on the resource."
  type = map(object({
    name = optional(string, null)
    role_assignments = optional(map(object({
      role_definition_id_or_name             = string
      principal_id                           = string
      description                            = optional(string, null)
      skip_service_principal_aad_check       = optional(bool, false)
      condition                              = optional(string, null)
      condition_version                      = optional(string, null)
      delegated_managed_identity_resource_id = optional(string, null)
    })), {})
    lock = optional(object({
      name = optional(string, null)
      kind = optional(string, null)
    }), {})
    tags                                    = optional(map(any), null)
    subnet_resource_id                      = string
    subresource_name                        = list(string)
    private_dns_zone_group_name             = optional(string, "default")
    private_dns_zone_resource_ids           = optional(set(string), [])
    application_security_group_associations = optional(map(string), {})
    private_service_connection_name         = optional(string, null)
    network_interface_name                  = optional(string, null)
    location                                = optional(string, null)
    inherit_tags                            = optional(bool, false)
    resource_group_name                     = optional(string, null)
    ip_configurations = optional(map(object({
      name               = string
      private_ip_address = string
    })), {})
  }))
  default = {}
}

variable "local_user" {
  description = "A map of local users to create on the storage account."
  type = map(object({
    home_directory       = optional(string)
    name                 = string
    ssh_key_enabled      = optional(bool)
    ssh_password_enabled = optional(bool)
    permission_scope = optional(list(object({
      resource_name = string
      service       = string
      permissions = object({
        create = optional(bool)
        delete = optional(bool)
        list   = optional(bool)
        read   = optional(bool)
        write  = optional(bool)
      })
    })))
    ssh_authorized_key = optional(list(object({
      description = optional(string)
      key         = string
    })))
    timeouts = optional(object({
      create = optional(string)
      delete = optional(string)
      read   = optional(string)
      update = optional(string)
    }))
  }))
  default = {}
}

variable "diagnostic_settings_storage_account" {
  description = "A map of diagnostic settings to create on the Storage Account."
  type = map(object({
    name                                     = optional(string, null)
    log_categories                           = optional(set(string))
    log_groups                               = optional(set(string), ["allLogs"])
    metric_categories                        = optional(set(string))
    log_analytics_destination_type           = optional(string, "Dedicated")
    workspace_resource_id                    = optional(string, null)
    storage_account_resource_id              = optional(string, null)
    log_analytics_workspace_id               = optional(string, null)
    event_hub_authorization_rule_resource_id = optional(string, null)
    event_hub_name                           = optional(string, null)
    marketplace_partner_resource_id          = optional(string, null)
  }))
  default = {}
}

variable "diagnostic_settings_blob" {
  description = "A map of diagnostic settings to create on the Blob Storage within storage account."
  type = map(object({
    name                                     = optional(string, null)
    log_categories                           = optional(set(string))
    log_groups                               = optional(set(string), ["allLogs"])
    metric_categories                        = optional(set(string))
    log_analytics_destination_type           = optional(string, "Dedicated")
    workspace_resource_id                    = optional(string, null)
    storage_account_resource_id              = optional(string, null)
    log_analytics_workspace_id               = optional(string, null)
    event_hub_authorization_rule_resource_id = optional(string, null)
    event_hub_name                           = optional(string, null)
    marketplace_partner_resource_id          = optional(string, null)
  }))
  default = {}
}

variable "diagnostic_settings_file" {
  description = "A map of diagnostic settings to create on the Azure Files Storage within storage account."
  type = map(object({
    name                                     = optional(string, null)
    log_categories                           = optional(set(string))
    metric_categories                        = optional(set(string))
    log_analytics_destination_type           = optional(string, "Dedicated")
    workspace_resource_id                    = optional(string, null)
    storage_account_resource_id              = optional(string, null)
    log_analytics_workspace_id               = optional(string, null)
    event_hub_authorization_rule_resource_id = optional(string, null)
    event_hub_name                           = optional(string, null)
    marketplace_partner_resource_id          = optional(string, null)
  }))
  default = {}
}

variable "diagnostic_settings_queue" {
  description = "A map of diagnostic settings to create on the Queue Storage within storage account."
  type = map(object({
    name                                     = optional(string, null)
    log_categories                           = optional(set(string))
    metric_categories                        = optional(set(string))
    log_analytics_destination_type           = optional(string, "Dedicated")
    workspace_resource_id                    = optional(string, null)
    storage_account_resource_id              = optional(string, null)
    log_analytics_workspace_id               = optional(string, null)
    event_hub_authorization_rule_resource_id = optional(string, null)
    event_hub_name                           = optional(string, null)
    marketplace_partner_resource_id          = optional(string, null)
  }))
  default = {}
}

variable "diagnostic_settings_table" {
  description = "A map of diagnostic settings to create on the Table Storage within storage account."
  type = map(object({
    name                                     = optional(string, null)
    log_categories                           = optional(set(string))
    metric_categories                        = optional(set(string))
    log_analytics_destination_type           = optional(string, "Dedicated")
    workspace_resource_id                    = optional(string, null)
    storage_account_resource_id              = optional(string, null)
    log_analytics_workspace_id               = optional(string, null)
    event_hub_authorization_rule_resource_id = optional(string, null)
    event_hub_name                           = optional(string, null)
    marketplace_partner_resource_id          = optional(string, null)
  }))
  default = {}
}

variable "table_encryption_key_type" {
  description = "(Optional) The encryption type of the table service. Possible values are `Service` and `Account`. Changing this forces a new resource to be created. Default value is `Service`."
  type        = string
  default     = null
}

variable "queue_encryption_key_type" {
  description = "(Optional) The encryption type of the queue service. Possible values are `Service` and `Account`. Changing this forces a new resource to be created. Default value is `Service`."
  type        = string
  default     = null
}

variable "enable_telemetry" {
  description = "This variable controls whether or not telemetry is enabled for the module."
  type        = bool
  default     = true
}

variable "timeouts" {
  description = "Timeouts for the storage account resource."
  type = object({
    create = optional(string)
    delete = optional(string)
    read   = optional(string)
    update = optional(string)
  })
  default = null
}