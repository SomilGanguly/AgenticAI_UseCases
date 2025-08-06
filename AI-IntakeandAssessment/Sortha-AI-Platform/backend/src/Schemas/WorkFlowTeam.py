from database import Base
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

class WorkFlowTeam(Base):
    __tablename__ = 'workflow_team'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workflow_id: Mapped[int] = mapped_column(Integer, ForeignKey('workflow.id'), nullable=False)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey('team.id'), nullable=False)

    def __repr__(self):
        return f'WorkFlowTeam(id={self.id}, workflow_id={self.workflow_id}, team_id={self.team_id})'