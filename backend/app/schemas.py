from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "operator"

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

class BlockCreate(BaseModel):
    name: str
    location: str
    status: str = "free"
    zone: str
    track_health: float = 100.0

class TrainCreate(BaseModel):
    train_number: str
    train_name: str
    train_type: str
    origin: str
    destination: str
    scheduled_departure: datetime
    scheduled_arrival: datetime
    passenger_load: float = 0.0

class AlertCreate(BaseModel):
    title: str
    description: str
    severity: str
    alert_type: str
    block_id: Optional[int] = None
    train_id: Optional[int] = None
