from database import Base
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship, backref, attribute_keyed_dict

class Folder(Base):
    __tablename__ = 'folder'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_folder_id: Mapped[int] = mapped_column(Integer, ForeignKey('folder.id'), nullable=True)
    owner_team_id: Mapped[int] = mapped_column(Integer, ForeignKey('team.id'), nullable=False)

    parent_folder: Mapped['Folder'] = relationship('Folder', back_populates='subfolders', remote_side=[id])
    subfolders: Mapped[list['Folder']] = relationship('Folder', back_populates='parent_folder')
    files: Mapped[list['File']] = relationship('File', back_populates='folder')
    owner_team: Mapped['Team'] = relationship('Team', foreign_keys='Folder.owner_team_id')

    def __repr__(self):
        return f"Folder(id='{self.id}', name='{self.name}', parent_folder_id='{self.parent_folder_id}', owner_team_id='{self.owner_team_id}, subfolders={self.subfolders}, owner_team={self.owner_team}, files={self.files})')"