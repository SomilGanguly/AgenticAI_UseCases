from pydantic import BaseModel, Field

class ResourceConfig(BaseModel):
    config_type: str = Field(description="Type of configuration, e.g. Memory, CPU, etc.")
    value: str = Field(description="Value of the configuration, e.g. '16GB', '4 vCPUs', etc.")
    comments: str = Field(description="Optional comments or notes about the configuration")
    reason: str = Field(description="Reason for the configuration, e.g. 'High performance required', 'Cost optimization', etc.")
    # transcript_reference: str = Field(description="Reference to the transcript section that supports this configuration")

class ResourceConfig(BaseModel):
    resource_type: str = Field(description="Type of the resource, e.g., 'EC2', 'S3', etc.")
    config: list[ResourceConfig] = Field(description="Configuration of the resource")
    best_fitting_sku: str = Field(description="Best fitting SKU for the resource")
    comments: str = Field(description="Optional comments or notes about the resource")

class TranscriptConfig(BaseModel):
    source_path: str = ''
    content: str = ''

class Resources(BaseModel):
    resources: list[ResourceConfig] = Field(description="List of resources extracted from the transcript")

class YesOrNo(BaseModel):
    output: bool = Field(description="Indicates if the condition is met")

class TerraformAttribute(BaseModel):
    name: str = Field(description="Name of the Terraform attribute, e.g., 'ami', 'instance_type', etc.")
    value: str = Field(description="Value of the Terraform attribute, e.g., 'ami-12345678', 't2.micro', etc.")
    comments: str = Field(description="Optional comments or notes about the attribute")
    reason: str = Field(description="Reason for the attribute, e.g., 'Required for instance creation', 'Cost optimization', etc.")

class TerraformDynamicBlock(BaseModel):
    block_type: str = Field(description="Type of dynamic block, e.g., 'for_each', 'count', etc.")
    content: list[TerraformAttribute] = Field(description="List of attributes within the dynamic block")

class TerraformConfig(BaseModel):
    block_type: str = Field(description="Type of Terraform block, e.g., 'resource', 'data', etc.")
    resource_type: str = Field(description="Type of the resource, e.g., 'aws_instance', 'azurerm_virtual_machine', etc.")
    resource_name: str = Field(description="Name of the resource in Terraform configuration")
    attributes: list[TerraformAttribute] = Field(description="List of attributes for the resource")
    dynamic_blocks: list[TerraformDynamicBlock] = Field(description="List of dynamic blocks within the resource")

class TerraformResourceList(BaseModel):
    resources: list[TerraformConfig] = Field(description="List of Terraform resources")

class TerraformCode(BaseModel):
    path: str = Field(description="Path to the generated Terraform code file")
    content: str = Field(description="Generated Terraform code based on the resources and configurations")
    purpose: str = Field(description="Purpose of the Terraform code, e.g., 'Provisioning Azure resources based on AWS configuration'")

class TerraFormCodeStructure(BaseModel):
    content: list[TerraformCode] = Field(description="List of Terraform resources")

class State(BaseModel):
    transcript: TranscriptConfig
    aws_resources: list[ResourceConfig] = []
    azure_resources: list[ResourceConfig] = []
    terraform_resources: list[TerraformConfig] = []
    retry_count: int = 0
    retry_limit: int = 3
    terraform_code: list[TerraformCode] = []