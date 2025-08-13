output "vnet_id" {
  description = "The id of the newly created vNet"
  value       = module.virtual_network.vnet_id
}

output "vnet_name" {
  description = "The name of the newly created vNet"
  value       = module.virtual_network.vnet_name
}

output "vnet_location" {
  description = "The location of the newly created vNet"
  value       = module.virtual_network.vnet_location
}

output "vnet_address_space" {
  description = "The address space of the newly created vNet"
  value       = module.virtual_network.vnet_address_space
}

output "subnet_ids" {
  description = "The ids of the newly created subnets"
  value       = module.virtual_network.subnet_ids
}