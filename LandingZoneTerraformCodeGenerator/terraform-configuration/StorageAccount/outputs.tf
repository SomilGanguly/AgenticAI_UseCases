output "id" {
  description = "The ID of the Storage Account."
  value       = module.storage_account.id
}

output "name" {
  description = "The name of the storage account."
  value       = module.storage_account.name
}

output "private_endpoints" {
  description = "A map of private endpoints. The map key is the supplied input to var.private_endpoints. The map value is the entire azurerm_private_endpoint resource."
  value       = module.storage_account.private_endpoints
}

output "queues" {
  description = "Map of storage queues that are created."
  value       = module.storage_account.queues
}

output "resource" {
  description = "This is the full resource output for the Storage Account resource."
  value       = module.storage_account.resource
}

output "tables" {
  description = "Map of storage tables that are created."
  value       = module.storage_account.tables
}

output "containers" {
  description = "Map of storage containers"
  value       = module.storage_account.containers
}