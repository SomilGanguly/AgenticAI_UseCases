from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import get_db
from sqlalchemy.orm import Session
from src.Schemas.Workflow import Workflow
from src.Services.SorthaAI.SorthaAIService import SorthaAIService
from ..Models.Workflow import CreateWorkflowExecutionRequest
from ..Services.GlobalService.GlobalService import GlobalService
from ..Utils.Serializer import addable_values_dict_to_json

router = APIRouter()

class WorkflowCreate(BaseModel):
    name: str
    description: str
    
class WorkflowResponse(BaseModel):
    id: int
    name: str
    description: str
    
# @router.post("/", response_model=WorkflowResponse)
# async def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db)):
#     db_workflow = db.query(Workflow).filter(Workflow.name == workflow.name).first()
#     if db_workflow:
#         raise HTTPException(status_code=400, detail="Workflow with this name already exists")
#     db_workflow = Workflow(name=workflow.name, description=workflow.description)
#     db.add(db_workflow)
#     db.commit()
#     db.refresh(db_workflow)
#     return db_workflow


@router.get('/list')
async def get_all_workflows(db: Session = Depends(get_db)):
    db_workflows = db.query(Workflow).all()
    return db_workflows

# not required not. Implemented at sortha workflow registration in init phase.
# @router.post('/create')
# async def create_workflow(workflow: CreateWorkflowRequest, db: Session = Depends(get_db)):
#     new_workflow = Workflow(
#         name=workflow.name,
#         description=workflow.description,
#         input_schema=str(workflow.input_schema),
#         output_schema=str(workflow.output_schema)
#     )
#     db.add(new_workflow)
#     db.commit()
#     db.refresh(new_workflow)
#     return new_workflow

@router.post("/execute/{workflow_id}")
async def create_execution(response: CreateWorkflowExecutionRequest, workflow_id: int):
    logger = GlobalService.get_instance().get_logService()
    from src.Services.SorthaAI.SorthaAIService import SorthaAIService
    ai_service: SorthaAIService = SorthaAIService.get_instance()
    workflow_state = ai_service.get_workflow_state_instance(workflow_id, **response.input_data)
    
    # Sample input
    '''
{
    "workflow_id":1,
    "input_data":{
        "inputs":{
            "transcript_file":{
                "type":"text",
                "file_id":1
            }
        }
    }
}
    '''
    request_id = ai_service.invoke_workflow(workflow_id, workflow_state)
    return {
        'request_id': request_id,
    }

@router.get("/get_status/{request_id}")
async def get_status(request_id: str):
    from src.Services.SorthaAI.SorthaAIService import SorthaAIService
    ai_service: SorthaAIService = SorthaAIService.get_instance()
    execution_status = ai_service.get_execution_status(request_id)
    return {
        "request_id": request_id,
        "status": execution_status,
        "result": ai_service.get_execution_result(request_id)
    }

@router.get('/test/{request_id}')
async def test(request_id: str):
    from src.Services.SorthaAI.SorthaAIService import SorthaAIService
    ai_service: SorthaAIService = SorthaAIService.get_instance()
    execution_status = ai_service.get_execution_status(request_id)
    res = ai_service.get_execution_result(request_id)
    print(addable_values_dict_to_json(res))
    return 'hello'