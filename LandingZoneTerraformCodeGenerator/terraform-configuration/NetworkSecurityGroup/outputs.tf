output "network_security_group_id" {
  description = "The ID of the Network Security Group."
  value       = module.network_security_group.id
}

output "network_security_group_name" {
  description = "The name of the Network Security Group."
  value       = module.network_security_group.name
}

output "network_security_group_resource_group" {
  description = "The resource group of the Network Security Group."
  value       = module.network_security_group.resource_group_name
}

output "network_security_group_location" {
  description = "The Azure location of the Network Security Group."
  value       = module.network_security_group.location
}

output "network_security_group_rules" {
  description = "The rules of the Network Security Group."
  value       = module.network_security_group.rules
}

output "network_security_group_tags" {
  description = "The tags assigned to the Network Security Group."
  value       = module.network_security_group.tags
}