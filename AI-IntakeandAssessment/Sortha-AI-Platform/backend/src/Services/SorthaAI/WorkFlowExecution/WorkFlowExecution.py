from ..WorkFlow.WorkFlowBase import WorkFlowBase
from ..Models.ExecutionState import Status as ExecutionStatus
from ..WorkFlow.StateBase import StateBase
from .FileParser import FileParser

import threading
from uuid import uuid4

class WorkFlowExecution:
    def __init__(self, workflow: WorkFlowBase):
        self.workflow = workflow

    def _threaded_invoke(self, state: StateBase, request_id, service):
        service.update_execution_state(request_id, ExecutionStatus.running)
        
        try:
            fp = FileParser(state)
            state = fp.execute()

            # Trigger the workflow execution
            result = self.workflow.invoke(state)
            service.update_execution_state_with_result(request_id, result)
        except Exception as e:
            service.update_execution_state_with_error(request_id, str(e))
        

    def execute(self, state: StateBase, service):
        request_id = str(uuid4())

        service.create_workflow_execution_state(request_id)
        threading.Thread(target=self._threaded_invoke, args=(state,request_id,service,)).start()
        return request_id