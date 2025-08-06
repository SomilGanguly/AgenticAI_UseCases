from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from database import Base
from .Folder import Folder
from .Team import Team

class File(Base):
    __tablename__ = 'file'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    creation_timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    parent_folder_id: Mapped[int] = mapped_column(Integer, ForeignKey('folder.id'), nullable=True)
    owner_team_id: Mapped[int] = mapped_column(Integer, ForeignKey('team.id'), nullable=False)
    file_physcial_address: Mapped[str] = mapped_column(String(255), nullable=False)

    folder: Mapped['Folder'] = relationship('Folder', back_populates='files')
    # owner_team: Mapped['Team'] = relationship('Team', backref='', foreign_keys='File.owner_team_id')

    def __repr__(self):
        return f'File(id={self.id}, name="{self.name}", size={self.size}, creation_timestamp={self.creation_timestamp}, parent_folder_id={self.parent_folder_id}, owner_team_id={self.owner_team_id})'