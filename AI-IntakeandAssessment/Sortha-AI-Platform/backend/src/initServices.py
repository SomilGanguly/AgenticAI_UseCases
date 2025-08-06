from src.Services.SorthaAI.AIClient.AzureChatOpenAI import AzureChatOpenAI
from os import getenv
from database import engine, Base

from src.Schemas import (
    File,
    Folder,
    Team,
    User,
    UserTeam,
    Workflow,
    WorkflowRun,
    WorkFlowTeam
)

def createOpenAIClient():
    return AzureChatOpenAI(
        deployment_name=getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
        model_name=getenv('AZURE_OPENAI_MODEL_NAME'),
        temperature=float(getenv('AZURE_OPENAI_TEMPERATURE', 0.7)),
        api_key=getenv('AZURE_OPENAI_API_KEY'),
        azure_endpoint=getenv('AZURE_OPENAI_ENDPOINT'),
        api_version=getenv('AZURE_OPENAI_API_VERSION', '2025-01-01-preview')
    )

def registerWorkflows():
    from src.Services.GlobalService.GlobalService import GlobalService
    from src.Services.SorthaAI.SorthaAIService import SorthaAIService
    from src.Workflows.TranscriptAwsToAzure import WorkFlow, State

    GlobalService.get_instance().get_sorthDBService().clear_db()
    llm = createOpenAIClient()
    ai = SorthaAIService(llm)
    ai.register_workflow('aif', 'converts transcript to aif', State.State, WorkFlow.TranscriptToAIF)

def initGlobalService():
    from src.Services.GlobalService.GlobalService import GlobalService
    global_service = GlobalService()

def initLoggerService():
    from src.Services.GlobalService.GlobalService import GlobalService
    from src.Services.LogPipe.LogPipe import LogPipe, LogLevel

    log_pipe = LogPipe()
    log_pipe.set_log_level(LogLevel.ALL)
    GlobalService.get_instance().register(log_pipe)

def initSorthaDBService():
    from src.Services.GlobalService.GlobalService import GlobalService
    from src.Utils.Sortha import SorthaDBService
    from database import get_db

    global_service = GlobalService.get_instance()
    sorthadb_service = SorthaDBService(next(get_db()))
    global_service.register(sorthadb_service)

def initFileService():
    from src.Services.GlobalService.GlobalService import GlobalService
    from src.Services.FileService.LocalFileService import LocalFileService
    base_path = getenv('LOCAL_FILE_SERVICE_BASE_PATH', './local_files')
    fs = LocalFileService(base_path=base_path)
    # fs.clear_all_files()
    GlobalService.get_instance().register(fs)

def init_db():
    # Base.metadata.drop_all(bind=engine)  # Drop existing tables
    # print("Dropping existing tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")

def test():
    from src.Services.WorkflowLoaderService.WorkflowLoaderService import WorkflowLoaderService
    wls = WorkflowLoaderService.get_instance()
    wls.set_base_location('./src/tempWorkflows')
    wls.refresh()
    wls.reload_all_workflows()

    from src.Services.GlobalService.GlobalService import GlobalService
    from src.Services.SorthaAI.SorthaAIService import SorthaAIService
    from src.Workflows.TranscriptAwsToAzure import WorkFlow, State

    GlobalService.get_instance().get_sorthDBService().clear_db()
    llm = createOpenAIClient()
    ai = SorthaAIService(llm)
    for workflow in wls.get_all_workflows():
        # print(f"Registering workflow: {workflow[0]}")
        ai.register_workflow(*workflow)
    # ai.register_workflow('aif', 'converts transcript to aif', State.State, WorkFlow.TranscriptToAIF)

def init():
    # Order of initialization matters
    init_db()

    initGlobalService()
    initLoggerService()
    initSorthaDBService()
    initFileService()
    
    # registerWorkflows()
    test()