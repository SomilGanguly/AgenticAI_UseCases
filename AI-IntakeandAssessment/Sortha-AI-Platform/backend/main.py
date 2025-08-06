from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Response

# Route imports
# from src.Routers.User import router as user_router
from src.Routers.File import router as file_router
from src.Routers.Workflow import router as workflow_router
# from src.Routers.Execution import router as execution_router
from src.Routers import (
    Team as TeamRouter
)

# Application initialization
from dotenv import load_dotenv
from src.initServices import init
from os import getenv

load_dotenv(getenv('ENV_FILE', './dev.env'))
init()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(user_router, prefix="/api/users", tags=["users"])
app.include_router(file_router, prefix="/api/files", tags=["files"])
app.include_router(workflow_router, prefix="/api/workflows", tags=["workflows"])
# app.include_router(execution_router, prefix="/api/executions", tags=["executions"])
app.include_router(TeamRouter.router, prefix="/api/team", tags=["team"])


# These are testing endpoints for initial testing of the SorthaAIService and its thread management services
@app.get("/testing1")
async def testing1(response: Response):
    from src.Services.SorthaAI.SorthaAIService import SorthaAIService
    ai_service: SorthaAIService = SorthaAIService.get_instance()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    workflow_state = ai_service.get_workflow_state_instance(
        1,
        transcript={
            'source_path': 'C:\\Users\\rohanverma\\OneDrive - Microsoft\\Desktop\\dev\\Infra and Sec COE\\sortha\\.dontCommit\\inputs\\rohanRohonTranscriptTest.txt'
        },
        retry_limit=5
    )
    request_id = ai_service.invoke_workflow(1, workflow_state)
    return {
        'request_id': request_id,
    }

@app.get("/testing2/{request_id}")
async def testing2(request_id: str):
    from src.Services.SorthaAI.SorthaAIService import SorthaAIService
    ai_service: SorthaAIService = SorthaAIService.get_instance()
    execution_status = ai_service.get_execution_status(request_id)
    return {
        "request_id": request_id,
        "status": execution_status,
        "result": ai_service.get_execution_result(request_id)
    }
