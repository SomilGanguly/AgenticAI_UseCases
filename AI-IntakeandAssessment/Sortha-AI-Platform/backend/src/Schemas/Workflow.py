from sqlalchemy import Column, Integer, String, Table
from sqlalchemy.orm import relationship, mapped_column, Mapped
from database import Base

class Workflow(Base):
    __tablename__ = 'workflow'
    
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String(255), nullable=False)
    description = mapped_column(String(500), nullable=True)
    input_schema = mapped_column(String(1000), nullable=False)
    output_schema = mapped_column(String(1000), nullable=False)

    teams: Mapped[list['Team']] = relationship('Team', secondary='workflow_team', back_populates='workflows')
    
    def __repr__(self):
        return f'Workflow(id={self.id}, name="{self.name}", description="{self.description}")'