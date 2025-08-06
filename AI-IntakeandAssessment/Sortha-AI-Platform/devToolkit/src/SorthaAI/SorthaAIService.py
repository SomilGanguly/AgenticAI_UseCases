from .WorkFlow.WorkFlowBase import WorkFlowBase
from .Models.ExecutionState import ExecutionState, Status as ExecutionStatus
from .WorkFlowExecution.WorkFlowExecution import WorkFlowExecution

from pydantic import BaseModel
from typing import Dict

from langchain_core.language_models.chat_models import BaseChatModel


class SorthaAIService:
    _instance = None
    def __init__(self, AIClient: BaseChatModel):
        if SorthaAIService._instance is not None:
            raise Exception("This class is a singleton!")
        SorthaAIService._instance = self
        self.llm: BaseChatModel = AIClient
        self.executions: Dict[str, ExecutionState] = {}

    def get_instance():
        if SorthaAIService._instance is None:
            raise Exception("SorthaAIService instance not initialized. Call initialize() first.")
        return SorthaAIService._instance
    
    def invoke_workflow(self, workflow: WorkFlowBase, input_state: BaseModel) -> str:
        wfe = WorkFlowExecution(workflow)
        request_id=wfe.execute(input_state, self)
        self.executions[request_id] = ExecutionState(execution_id=request_id)
        return request_id
    
    def get_execution_result(self, execution_id: str) -> WorkFlowExecution:
        if execution_id not in self.executions:
            raise ValueError(f"Execution ID '{execution_id}' does not exist.")
        
        execution = self.executions[execution_id]
        if execution.status == ExecutionStatus.completed:
            return execution.result
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

    def update_execution_state_with_error(self, execution_id: str, error: str):
        if execution_id not in self.executions:
            raise ValueError(f"Execution ID '{execution_id}' does not exist.")

        execution_state: ExecutionState = self.executions[execution_id]
        execution_state.error = error
        execution_state.status = ExecutionStatus.failed

    def get_execution_state(self, execution_id: str) -> ExecutionState:
        if execution_id not in self.executions:
            raise ValueError(f"Execution ID '{execution_id}' does not exist.")
        
        return self.executions[execution_id]



