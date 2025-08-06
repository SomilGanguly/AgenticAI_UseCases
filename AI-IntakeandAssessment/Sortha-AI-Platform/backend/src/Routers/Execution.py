from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import get_db
from sqlalchemy.orm import Session
from src.Schemas.Execution import Execution

class ExecutionCreate(BaseModel):
    workflow_id: int
    file_id: int
    
class ExecutionResponse(BaseModel):
    id: int
    workflow_id: int
    file_id: int
    
router = APIRouter()

@router.post("/", response_model=ExecutionResponse)
async def create_execution(execution: ExecutionCreate, db: Session = Depends(get_db)):
    db_execution = Execution(
        workflow_id=execution.workflow_id,
        file_id=execution.file_id
    )
    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)
    return db_execution