from src.Schemas.Workflow import Workflow
from src.Schemas.WorkflowRun import WorkflowRun, WorkflowRunStatus

class SorthaDBService:
    def __init__(self, db):
        self.db = db

    def clear_db(self):
        self.db.query(Workflow).delete()
        self.db.commit()

    def register_workflow(self, name, description, input_schema, output_schema) -> int:
        wf = Workflow(
            name=name,
            description=description,
            input_schema=input_schema,
            output_schema=output_schema
        )
        existing_workflow = self.db.query(Workflow).filter_by(name=name).first()
        if existing_workflow:
            self.db.delete(existing_workflow)
        self.db.add(wf)
        self.db.commit()
        self.db.refresh(wf)
        return wf.id

    def create_workflow_run(self, workflow_id, input_data, triggered_by, team_id, request_id):
        workflow_run = WorkflowRun(
            workflow_id=workflow_id,
            status=WorkflowRunStatus.RUNNING,
            input_data=input_data,
            output_data=None,  # Initially set to None, will be updated later
            triggered_by=triggered_by,  # Assuming a default user ID for now
            team_id=team_id,  # Assuming a default team ID for now
            request_id=request_id  # This can be set later if needed
        )
        self.db.add(workflow_run)
        self.db.commit()

    def update_execution_state_with_result(self, request_id, result):
        workflow_run = self.db.query(WorkflowRun).filter_by(request_id=request_id).first()
        if workflow_run:
            workflow_run.status = WorkflowRunStatus.COMPLETED
            workflow_run.output_data = result
            self.db.commit()
        else:
            raise ValueError(f"Workflow run with request ID '{request_id}' not found.")
    
    def update_execution_state_with_error(self, request_id, error_message):
        workflow_run = self.db.query(WorkflowRun).filter_by(request_id=request_id).first()
        if workflow_run:
            workflow_run.status = WorkflowRunStatus.FAILED
            workflow_run.output_data = error_message
            self.db.commit()
        else:
            raise ValueError(f"Workflow run with request ID '{request_id}' not found.")