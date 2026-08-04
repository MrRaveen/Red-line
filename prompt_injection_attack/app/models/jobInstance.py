from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base

class JobInstance(Base):
    __tablename__ = "jobs"
    
    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    job_name = Column(String(255), nullable=False)
    created_date = Column(DateTime, server_default=func.now(), nullable=False)
    description = Column(String(255), nullable=False)
    job_cat = Column(String(255), nullable=False, index=True)
    job_status = Column(String(50), nullable=False, default="pending")
    userID = Column(Integer, ForeignKey("users.ID"), nullable=False, index=True)