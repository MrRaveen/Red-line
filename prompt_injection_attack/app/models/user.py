from sqlalchemy import Column, Integer, String
from .base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
