from pydantic import BaseModel, Field
from .SorthaDevKit.StateBase import StateBase

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

class State(StateBase):
    transcript: str = None
    aws_resources: list[ResourceConfig] = []
    azure_resources: list[ResourceConfig] = []
    retry_count: int = 0
    retry_limit: int = 3

class Resources(BaseModel):
    resources: list[ResourceConfig] = Field(description="List of resources extracted from the transcript")

class YesOrNo(BaseModel):
    output: bool = Field(description="Indicates if the condition is met")