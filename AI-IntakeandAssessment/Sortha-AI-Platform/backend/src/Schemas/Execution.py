# from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
# from sqlalchemy.orm import relationship
# from datetime import datetime, timezone
# from database import Base


# class Execution(Base):
#     __tablename__ = 'execution'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
#     workflow_id = Column(Integer, ForeignKey('workflows.id'), nullable=False)
#     status = Column(String(50), default='pending', nullable=False)
#     file = relationship("File", back_populates="executions")
#     workflow = relationship("Workflow", back_populates="executions")
    
#     finished_at = Column(DateTime, nullable=True)
#     created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
#     def __repr__(self):
#         return f"<Execution(id={self.id}, file_id={self.file_id}, workflow_id={self.workflow_id})>"