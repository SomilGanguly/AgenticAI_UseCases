from .WorkFlow.WorkFlowBase import WorkFlowBase
from .Models.ExecutionState import ExecutionState, Status as ExecutionStatus
from .WorkFlowExecution.WorkFlowExecution import WorkFlowExecution
from ..GlobalService.GlobalService import GlobalService

from pydantic import BaseModel
from typing import Dict

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.pregel.io import AddableValuesDict
import json

class SorthaAIService:
    _instance = None
    def __init__(self, AIClient: BaseChatModel):
        if SorthaAIService._instance is not None:
            raise Exception("This class is a singleton!")
        SorthaAIService._instance = self
        self.llm: BaseChatModel = AIClient
        self.workflows: Dict[str, Dict] = {}
        self.executions: Dict[str, ExecutionState] = {}

    def get_instance():
        if SorthaAIService._instance is None:
            raise Exception("SorthaAIService instance not initialized. Call initialize() first.")
        return SorthaAIService._instance

    def register_workflow(self, workflow_name: str, workflow_description: str, workflow_state_class: BaseModel, workflow_class: WorkFlowBase, input_config: dict):
        workflow: WorkFlowBase = workflow_class(self.llm)
        workflow.createStateGraph(workflow_state_class)
        workflow.buildGraph()
        wf_id = GlobalService.get_instance() \
            .get_sorthDBService() \
            .register_workflow(workflow_name, workflow_description, json.dumps(input_config), '')
        
        self.workflows[wf_id] = {
            'workflow': workflow,
            'state_class': workflow_state_class
        }

    def get_all_workflows(self) -> list:
        arr = []
        for workflow_id, workflow_info in self.workflows.items():
            arr.append({
                'id': workflow_id
            })
        return arr

    def get_workflow_state_instance(self, workflow_id: id, **kwargs) -> BaseModel:
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow with id '{workflow_id}' is not registered.")
        
        workflow_info = self.workflows[workflow_id]
        state_class = workflow_info['state_class']
        return state_class(**kwargs)
    
    def invoke_workflow(self, workflow_id: int, input_state: BaseModel) -> str:
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow with id '{workflow_id}' is not registered.")
        
        workflow_info = self.workflows[workflow_id]
        workflow = workflow_info['workflow']
        
        if not isinstance(input_state, workflow_info['state_class']):
            raise TypeError(f"Input state must be an instance of {workflow_info['state_class']}")

        wfe = WorkFlowExecution(workflow)
        request_id=wfe.execute(input_state, self)
        self.executions[request_id] = ExecutionState(execution_id=request_id)
        GlobalService.get_instance() \
            .get_sorthDBService() \
            .create_workflow_run(workflow_id, 'input_state.model_dump_json()', 1, 1, request_id)
        return request_id
    
    def get_execution_result(self, execution_id: str) -> AddableValuesDict:
        if execution_id not in self.executions:
            raise ValueError(f"Execution ID '{execution_id}' does not exist.")
        
        execution = self.executions[execution_id]
        if execution.status == ExecutionStatus.completed:
            if 'output' not in execution.result:
                return execution.result
            return execution.result['output']
        elif execution.status == ExecutionStatus.failed:
            return execution.error
        else:
            return None  # Execution is still running or not started
    
    def get_execution_status(self, execution_id: str) -> ExecutionStatus:
        if execution_id not in self.executions:
            raise ValueError(f"Execution ID '{execution_id}' does not exist.")
        
        return self.executions[execution_id].status
    
    def create_workflow_execution_state(self, execution_id: str):
        if execution_id in self.executions:
            raise ValueError(f"Execution ID '{execution_id}' already exists.")
        
        execution_state = ExecutionState(execution_id=execution_id)
        self.executions[execution_id] = execution_state

        return execution_state
    
    def update_execution_state(self, execution_id: str, status: ExecutionStatus):
        if execution_id not in self.executions:
            raise ValueError(f"Execution ID '{execution_id}' does not exist.")

        execution_state: ExecutionState = self.executions[execution_id]
        execution_state.status = status

    def update_execution_state_with_result(self, execution_id: str, result: BaseModel):
        if execution_id not in self.executions:
            raise ValueError(f"Execution ID '{execution_id}' does not exist.")

        execution_state: ExecutionState = self.executions[execution_id]
        execution_state.result = result
        execution_state.status = ExecutionStatus.completed
        GlobalService.get_instance() \
            .get_sorthDBService() \
            .update_execution_state_with_result(execution_id, 'this is a placeholder for result serialization')

    def update_execution_state_with_error(self, execution_id: str, error: str):
        if execution_id not in self.executions:
            raise ValueError(f"Execution ID '{execution_id}' does not exist.")

        execution_state: ExecutionState = self.executions[execution_id]
        execution_state.error = error
        execution_state.status = ExecutionStatus.failed
        GlobalService.get_instance() \
            .get_sorthDBService() \
            .update_execution_state_with_error(execution_id, error)

    def get_execution_state(self, execution_id: str) -> ExecutionState:
        if execution_id not in self.executions:
            raise ValueError(f"Execution ID '{execution_id}' does not exist.")
        
        return self.executions[execution_id]



