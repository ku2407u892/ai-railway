from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="operator")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Block(Base):
    __tablename__ = "blocks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    location = Column(String)
    status = Column(String, default="free")
    zone = Column(String)
    track_health = Column(Float, default=100.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    trains = relationship("Train", back_populates="current_block")

class Train(Base):
    __tablename__ = "trains"
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String, unique=True, index=True)
    train_name = Column(String)
    train_type = Column(String)
    current_block_id = Column(Integer, ForeignKey("blocks.id"), nullable=True)
    origin = Column(String)
    destination = Column(String)
    scheduled_departure = Column(DateTime)
    scheduled_arrival = Column(DateTime)
    delay_minutes = Column(Integer, default=0)
    status = Column(String, default="on_time")
    passenger_load = Column(Float, default=0.0)
    priority_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    current_block = relationship("Block", back_populates="trains")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    severity = Column(String)
    alert_type = Column(String)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=True)
    train_id = Column(Integer, ForeignKey("trains.id"), nullable=True)
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class OptimizationLog(Base):
    __tablename__ = "optimization_logs"
    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String)
    description = Column(Text)
    delay_saved_minutes = Column(Integer, default=0)
    efficiency_gain = Column(Float, default=0.0)
    executed_by = Column(String, default="AI")
    created_at = Column(DateTime, default=datetime.utcnow)
