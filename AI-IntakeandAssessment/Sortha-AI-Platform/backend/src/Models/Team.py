from pydantic import BaseModel, Field

class CreateTeamRequest(BaseModel):
    name: str = Field(..., description="Name of the team")
    description: str = Field(..., description="Description of the team")

class CreateTeamResponse(BaseModel):
    id: int = Field(..., description="Unique identifier of the created team")
    name: str = Field(..., description="Name of the created team")
    description: str = Field(..., description="Description of the created team")

    def __str__(self):
        return f"Team(id={self.id}, name={self.name}, description={self.description})"
    
class RegisterWorkflowRequest(BaseModel):
    team_id: int = Field(..., description="ID of the team to register")
    workflow_id: int = Field(..., description="ID of the workflow to register")