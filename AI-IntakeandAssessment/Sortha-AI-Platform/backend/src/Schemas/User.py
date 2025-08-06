from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from database import Base
from datetime import datetime, timezone

class User(Base):
    __tablename__ = 'user'
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    teams: Mapped[list['Team']] = relationship('Team', secondary='user_team', back_populates='users')

    def __repr__(self):
        return f'User(id="{self.id}", name="{self.name}", email="{self.email}")'