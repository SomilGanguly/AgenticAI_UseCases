from database import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, Mapped, relationship

class Team(Base):
    __tablename__ = 'team'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)

    users: Mapped[list['User']] = relationship('User', secondary='user_team', back_populates='teams')
    workflows: Mapped[list['Workflow']] = relationship('Workflow', secondary='workflow_team', back_populates='teams')
    
    def __repr__(self):
        return f'Team(id={self.id}, name="{self.name}", description="{self.description}")'