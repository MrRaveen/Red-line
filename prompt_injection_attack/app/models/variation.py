from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base

class Variation(Base):
    __tablename__ = "variation"
    
    variationID = Column(Integer, primary_key=True, autoincrement=True)
    agent_thinking = Column(Text, nullable=True)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    res_stat_code = Column(String(50), nullable=True)
    created_time = Column(DateTime, server_default=func.now(), nullable=False)
    
    jobID = Column(Integer, ForeignKey("jobs.ID"), nullable=False, index=True)
