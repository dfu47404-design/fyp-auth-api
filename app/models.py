from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .db import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    age = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    foot_size = Column(Float, nullable=True)
    purpose = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
