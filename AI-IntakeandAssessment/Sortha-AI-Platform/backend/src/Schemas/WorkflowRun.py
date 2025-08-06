from database import Base
from sqlalchemy import Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy.sql import func
import enum

class WorkflowRunStatus(enum.Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class WorkflowRun(Base):
    __tablename__ = 'workflow_run'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workflow_id: Mapped[int] = mapped_column(Integer, ForeignKey('workflow.id'), nullable=False)
    status: Mapped[WorkflowRunStatus] = mapped_column(Enum(WorkflowRunStatus), nullable=False)
    last_updated: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    input_data: Mapped[str] = mapped_column(String(1000), nullable=False)
    output_data: Mapped[str] = mapped_column(String(1000), nullable=True)
    triggered_by: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey('team.id'), nullable=False)
    request_id: Mapped[str] = mapped_column(String(100), nullable=True)
    
    workflow = relationship('Workflow')

    def __repr__(self):
        return f'WorkflowRun(id={self.id}, workflow_id={self.workflow_id}, status={self.status}, last_updated={self.last_updated}, input_data="{self.input_data}", output_data="{self.output_data}", triggered_by={self.triggered_by})'