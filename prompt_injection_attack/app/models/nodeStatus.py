from sqlalchemy import Column, Integer, String, Text, ForeignKey
from .base import Base

class NodeStatus(Base):
    __tablename__ = "nodeStatus"
    
    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    node_name = Column(String(255), nullable=False)
    node_input = Column(Text, nullable=True)
    node_output = Column(Text, nullable=True)
    node_status = Column(String(50), nullable=False)
    
    jobID = Column(Integer, ForeignKey("jobs.ID"), nullable=False, index=True)
    variationID = Column(Integer, ForeignKey("variation.variationID"), nullable=True, index=True)
