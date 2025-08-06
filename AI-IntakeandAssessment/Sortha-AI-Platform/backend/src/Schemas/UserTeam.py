from database import Base
from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import mapped_column, Mapped

class UserTeam(Base):
    __tablename__ = 'user_team'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[String] = mapped_column(String, ForeignKey('user.id'), nullable=False)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey('team.id'), nullable=False)

    def __repr__(self):
        return f'UserTeam(id={self.id}, user_id={self.user_id}, team_id={self.team_id})'