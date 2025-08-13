output "resource_secrets" {
  description = "A map of secret objects. The map key is the supplied input to var.secrets. The map value is the entire azurerm_key_vault_secret resource."
  value       = module.keyvault.resource_secrets
  sensitive   = true
}

output "resource" {
  description = "The Key Vault resource."
  value       = module.keyvault.resource
}

output "resource_keys" {
  description = "A map of key objects. The map key is the supplied input to var.keys. The map value is the entire azurerm_key_vault_key resource."
  value       = module.keyvault.resource_keys
}