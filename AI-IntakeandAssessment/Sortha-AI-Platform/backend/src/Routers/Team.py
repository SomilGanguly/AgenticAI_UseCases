from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from ..Models.Team import CreateTeamRequest, CreateTeamResponse, RegisterWorkflowRequest
from ..Schemas.Team import Team
from ..Schemas.WorkFlowTeam import WorkFlowTeam
router = APIRouter()

@router.post("/")
def create_team(request: CreateTeamRequest, db: Session = Depends(get_db)):
    team = Team(
        name=request.name,
        description=request.description
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    newTeam = CreateTeamResponse(
        id=team.id,
        name=team.name,
        description=team.description
    )
    return newTeam


@router.post("/registerWorkflow")
def register_workflow(req: RegisterWorkflowRequest, db: Session = Depends(get_db)):
    new_workflow_team = WorkFlowTeam(
        team_id=req.team_id,
        workflow_id=req.workflow_id
    )
    db.add(new_workflow_team)
    db.commit()

    return {'workflows': db.query(Team).filter(Team.id == req.team_id).first().workflows}


@router.post("/addUser")
def add_user_to_team():
    '''
    Add a user to the specified team.
    '''
    raise NotImplementedError("This endpoint is not implemented yet.")

