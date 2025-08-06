from pydantic import BaseModel, Field

class CreateWorkflowRequest(BaseModel):
    name: str = Field(..., description="Name of the workflow")
    description: str = Field(..., description="Description of the workflow")
    input_schema: dict = Field(..., description="Input schema for the workflow")
    output_schema: dict = Field(..., description="Output schema for the workflow")

class CreateWorkflowExecutionRequest(BaseModel):
    workflow_id: int = Field(..., description="ID of the workflow to execute")
    input_data: dict = Field(..., description="Input data for the workflow execution")