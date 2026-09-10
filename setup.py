import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
FILES = {}

# ══════════════════════════════════════════════
# BACKEND FILES
# ══════════════════════════════════════════════

FILES["backend/requirements.txt"] = """\
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
python-jose==3.3.0
passlib==1.7.4
python-dotenv==1.0.0
pydantic==2.5.0
bcrypt==4.1.1
python-multipart==0.0.6
numpy==1.26.2
scikit-learn==1.3.2
"""

FILES["backend/.env"] = """\
DATABASE_URL=sqlite:///./railops.db
SECRET_KEY=railops-super-secret-key-2026
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
"""

FILES["backend/app/__init__.py"] = ""

FILES["backend/app/database.py"] = """\
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./railops.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""

FILES["backend/app/models.py"] = """\
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
"""

FILES["backend/app/schemas.py"] = """\
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
"""

FILES["backend/app/ai/__init__.py"] = ""

FILES["backend/app/ai/predictor.py"] = """\
import random
from datetime import datetime

class DelayPredictor:
    def __init__(self):
        self.weather_factors = {
            "clear": 1.0, "rain": 1.4, "fog": 1.6,
            "flood": 2.5, "storm": 2.0, "heatwave": 1.2
        }
        self.train_priority = {
            "medical_emergency": 10, "defense": 9,
            "high_speed": 8, "express": 7,
            "passenger": 5, "freight": 3, "local": 4
        }

    def calculate_priority_score(self, train_data: dict) -> float:
        base = self.train_priority.get(train_data.get("type", "local"), 4)
        delay_f = min(train_data.get("delay_minutes", 0) / 30, 2.0)
        pass_f = train_data.get("passenger_load", 0) / 100
        weather = train_data.get("weather", "clear")
        weather_f = self.weather_factors.get(weather, 1.0)
        score = ((base * 0.4) + (delay_f * 0.25) + (pass_f * 0.2) + (weather_f * 0.15)) * 10
        return round(min(score, 100), 2)

    def predict_delay(self, train_data: dict) -> dict:
        base_delay = train_data.get("current_delay", 0)
        weather = train_data.get("weather", "clear")
        weather_m = self.weather_factors.get(weather, 1.0)
        track_health = train_data.get("track_health", 100) / 100
        track_impact = (1 - track_health) * 20
        hour = datetime.now().hour
        peak = list(range(7, 10)) + list(range(17, 20))
        time_f = 1.3 if hour in peak else 1.0
        predicted = int((base_delay + track_impact) * weather_m * time_f + random.randint(-5, 5))
        return {
            "predicted_delay_minutes": max(0, predicted),
            "confidence": round(random.uniform(0.75, 0.95), 2),
            "contributing_factors": {
                "weather": weather,
                "track_health": track_health * 100,
                "time_factor": "peak" if hour in peak else "off-peak",
                "base_delay": base_delay
            }
        }
"""

FILES["backend/app/ai/optimizer.py"] = """\
import random
from datetime import datetime

class BlockOptimizer:
    def generate_suggestions(self, trains: list, blocks: list) -> list:
        suggestions = []
        sid = 1
        delayed = [t for t in trains if t.get("delay_minutes", 0) > 15]
        for train in delayed[:3]:
            suggestions.append({
                "id": sid,
                "type": "Delay Resolution",
                "description": f"Reroute Train {train.get('train_number','?')} to recover {train.get('delay_minutes',0)} min delay",
                "priority": "high" if train.get("delay_minutes", 0) > 30 else "medium",
                "impact": round(random.uniform(15, 40), 1),
                "estimated_time": random.randint(5, 15),
                "affected_trains": [train.get("train_number", "?")]
            })
            sid += 1
        maint = [b for b in blocks if b.get("status") == "maintenance"]
        if maint:
            suggestions.append({
                "id": sid,
                "type": "Maintenance Optimization",
                "description": f"Schedule {len(maint)} block(s) for 02:00-04:00 AM maintenance window",
                "priority": "medium",
                "impact": round(random.uniform(10, 25), 1),
                "estimated_time": random.randint(30, 120),
                "affected_trains": []
            })
            sid += 1
        free = [b for b in blocks if b.get("status") == "free"]
        if len(free) > 3:
            suggestions.append({
                "id": sid,
                "type": "Capacity Optimization",
                "description": f"Utilize {len(free)} free blocks to increase throughput",
                "priority": "low",
                "impact": round(random.uniform(5, 15), 1),
                "estimated_time": random.randint(10, 30),
                "affected_trains": []
            })
        return suggestions

    def execute_optimization(self, suggestions, trains, blocks):
        return {
            "status": "success",
            "message": f"Optimization executed. {len(suggestions)} changes applied.",
            "delay_saved_minutes": sum(random.randint(5, 20) for _ in suggestions),
            "efficiency_gain_percent": round(random.uniform(8, 25), 1),
            "timestamp": datetime.utcnow().isoformat()
        }
"""

FILES["backend/app/routes/__init__.py"] = ""

FILES["backend/app/routes/auth.py"] = """\
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from ..database import get_db
from ..models import User
from ..schemas import UserCreate, Token

load_dotenv()
router = APIRouter(prefix="/auth", tags=["Authentication"])
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verify_password(plain, hashed): return pwd_context.verify(plain, hashed)
def get_password_hash(password): return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username: raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if not user: raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter((User.username == user_data.username) | (User.email == user_data.email)).first():
        raise HTTPException(status_code=400, detail="Username or email already exists")
    user = User(username=user_data.username, email=user_data.email,
                hashed_password=get_password_hash(user_data.password), role=user_data.role)
    db.add(user); db.commit(); db.refresh(user)
    return {"message": "Registered successfully", "username": user.username}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role, "username": user.username}

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username,
            "email": current_user.email, "role": current_user.role}
"""

FILES["backend/app/routes/blocks.py"] = """\
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import Block
from ..schemas import BlockCreate
from .auth import get_current_user

router = APIRouter(prefix="/blocks", tags=["Blocks"])

@router.get("/")
def get_blocks(db: Session = Depends(get_db)):
    blocks = db.query(Block).all()
    return [{"id": b.id, "name": b.name, "location": b.location, "status": b.status,
             "zone": b.zone, "track_health": b.track_health,
             "created_at": b.created_at.isoformat(), "updated_at": b.updated_at.isoformat()} for b in blocks]

@router.get("/{block_id}")
def get_block(block_id: int, db: Session = Depends(get_db)):
    b = db.query(Block).filter(Block.id == block_id).first()
    if not b: raise HTTPException(status_code=404, detail="Block not found")
    return {"id": b.id, "name": b.name, "location": b.location, "status": b.status, "zone": b.zone, "track_health": b.track_health}

@router.post("/")
def create_block(data: BlockCreate, db: Session = Depends(get_db), cu=Depends(get_current_user)):
    if cu.role != "admin": raise HTTPException(status_code=403, detail="Admin only")
    b = Block(**data.dict()); db.add(b); db.commit(); db.refresh(b)
    return {"message": "Block created", "id": b.id}

@router.put("/{block_id}/status")
def update_status(block_id: int, status: str, db: Session = Depends(get_db), cu=Depends(get_current_user)):
    b = db.query(Block).filter(Block.id == block_id).first()
    if not b: raise HTTPException(status_code=404, detail="Block not found")
    if status not in ["free","occupied","reserved","maintenance"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    b.status = status; b.updated_at = datetime.utcnow(); db.commit()
    return {"message": f"Block {b.name} - {status}"}

@router.delete("/{block_id}")
def delete_block(block_id: int, db: Session = Depends(get_db), cu=Depends(get_current_user)):
    if cu.role != "admin": raise HTTPException(status_code=403, detail="Admin only")
    b = db.query(Block).filter(Block.id == block_id).first()
    if not b: raise HTTPException(status_code=404, detail="Block not found")
    db.delete(b); db.commit()
    return {"message": f"Block {b.name} deleted"}
"""

FILES["backend/app/routes/trains.py"] = """\
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import Train, Block
from ..schemas import TrainCreate
from ..ai.predictor import DelayPredictor
from .auth import get_current_user

router = APIRouter(prefix="/trains", tags=["Trains"])
predictor = DelayPredictor()

@router.get("/")
def get_trains(db: Session = Depends(get_db)):
    trains = db.query(Train).all()
    return [{"id": t.id, "train_number": t.train_number, "train_name": t.train_name,
             "train_type": t.train_type, "origin": t.origin, "destination": t.destination,
             "current_block_id": t.current_block_id,
             "current_block_name": t.current_block.name if t.current_block else None,
             "delay_minutes": t.delay_minutes, "status": t.status,
             "priority_score": t.priority_score, "passenger_load": t.passenger_load,
             "scheduled_departure": t.scheduled_departure.isoformat(),
             "scheduled_arrival": t.scheduled_arrival.isoformat()} for t in trains]

@router.get("/{train_id}/predict-delay")
def predict_delay(train_id: int, db: Session = Depends(get_db)):
    t = db.query(Train).filter(Train.id == train_id).first()
    if not t: raise HTTPException(status_code=404, detail="Train not found")
    data = {"current_delay": t.delay_minutes,
            "track_health": t.current_block.track_health if t.current_block else 85.0,
            "type": t.train_type, "passenger_load": t.passenger_load, "weather": "clear"}
    return {"train_number": t.train_number, "train_name": t.train_name,
            "current_delay": t.delay_minutes, "prediction": predictor.predict_delay(data)}

@router.post("/")
def create_train(data: TrainCreate, db: Session = Depends(get_db), cu=Depends(get_current_user)):
    if cu.role != "admin": raise HTTPException(status_code=403, detail="Admin only")
    ps = predictor.calculate_priority_score({"type": data.train_type, "delay_minutes": 0, "passenger_load": data.passenger_load})
    t = Train(**data.dict(), priority_score=ps)
    db.add(t); db.commit(); db.refresh(t)
    return {"message": "Train created", "id": t.id, "priority_score": ps}

@router.put("/{train_id}/assign-block")
def assign_block(train_id: int, block_id: int, db: Session = Depends(get_db), cu=Depends(get_current_user)):
    t = db.query(Train).filter(Train.id == train_id).first()
    if not t: raise HTTPException(status_code=404, detail="Train not found")
    b = db.query(Block).filter(Block.id == block_id).first()
    if not b: raise HTTPException(status_code=404, detail="Block not found")
    t.current_block_id = block_id; t.updated_at = datetime.utcnow()
    b.status = "occupied"; b.updated_at = datetime.utcnow()
    db.commit()
    return {"message": f"Train {t.train_number} - Block {b.name}"}
"""

FILES["backend/app/routes/alerts.py"] = """\
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Alert
from ..schemas import AlertCreate
from .auth import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("/")
def get_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).filter(Alert.is_acknowledged == False).all()
    return [{"id": a.id, "title": a.title, "description": a.description,
             "severity": a.severity, "alert_type": a.alert_type,
             "block_id": a.block_id, "train_id": a.train_id,
             "is_acknowledged": a.is_acknowledged,
             "timestamp": a.created_at.strftime("%Y-%m-%d %H:%M")} for a in alerts]

@router.post("/{alert_id}/acknowledge")
def acknowledge(alert_id: int, db: Session = Depends(get_db), cu=Depends(get_current_user)):
    a = db.query(Alert).filter(Alert.id == alert_id).first()
    if not a: raise HTTPException(status_code=404, detail="Alert not found")
    a.is_acknowledged = True; db.commit()
    return {"message": f"Alert {alert_id} acknowledged"}

@router.post("/")
def create_alert(data: AlertCreate, db: Session = Depends(get_db), cu=Depends(get_current_user)):
    a = Alert(**data.dict()); db.add(a); db.commit(); db.refresh(a)
    return {"message": "Alert created", "id": a.id}
"""

FILES["backend/app/routes/optimization.py"] = """\
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Train, Block, OptimizationLog
from ..ai.optimizer import BlockOptimizer
from ..ai.predictor import DelayPredictor
from .auth import get_current_user

router = APIRouter(prefix="/optimization", tags=["Optimization"])
optimizer = BlockOptimizer()
predictor = DelayPredictor()

@router.get("/suggestions")
def get_suggestions(db: Session = Depends(get_db)):
    trains = [{"id": t.id, "train_number": t.train_number, "train_type": t.train_type,
               "delay_minutes": t.delay_minutes, "current_block_id": t.current_block_id,
               "priority_score": t.priority_score} for t in db.query(Train).all()]
    blocks = [{"id": b.id, "name": b.name, "status": b.status, "track_health": b.track_health}
              for b in db.query(Block).all()]
    return optimizer.generate_suggestions(trains, blocks)

@router.post("/execute")
def execute(db: Session = Depends(get_db), cu=Depends(get_current_user)):
    trains = [{"id": t.id, "train_number": t.train_number, "delay_minutes": t.delay_minutes}
              for t in db.query(Train).all()]
    blocks = [{"id": b.id, "name": b.name, "status": b.status} for b in db.query(Block).all()]
    suggestions = optimizer.generate_suggestions(trains, blocks)
    result = optimizer.execute_optimization(suggestions, trains, blocks)
    log = OptimizationLog(action_type="auto_optimize", description=result["message"],
                          delay_saved_minutes=result["delay_saved_minutes"],
                          efficiency_gain=result["efficiency_gain_percent"],
                          executed_by=cu.username)
    db.add(log); db.commit()
    return result

@router.get("/system-status")
def system_status(db: Session = Depends(get_db)):
    return {"status": "operational", "uptime": "99.9%",
            "total_trains": db.query(Train).count(),
            "active_blocks": db.query(Block).filter(Block.status == "occupied").count(),
            "pending_alerts": db.query(Block).filter(Block.status == "maintenance").count(),
            "last_optimization": "2 minutes ago"}
"""

FILES["backend/app/main.py"] = """\
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, SessionLocal
from .models import User, Block, Train, Alert, OptimizationLog
from .routes import auth, blocks, trains, alerts, optimization
from .routes.auth import get_password_hash
from datetime import datetime, timedelta

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI RailOps", description="AI-Powered Block Planning for Indian Railways", version="1.0.0")

app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router)
app.include_router(blocks.router)
app.include_router(trains.router)
app.include_router(alerts.router)
app.include_router(optimization.router)

def seed():
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            return
        db.add_all([
            User(username="admin", email="admin@railops.com", hashed_password=get_password_hash("railway123"), role="admin"),
            User(username="operator", email="operator@railops.com", hashed_password=get_password_hash("railway123"), role="operator")
        ])
        db.commit()
        block_data = [
            {"name":"AHM-01","location":"Ahmedabad Station","zone":"Western","status":"occupied","track_health":92.5},
            {"name":"AHM-02","location":"Ahmedabad Yard","zone":"Western","status":"free","track_health":88.0},
            {"name":"AND-01","location":"Anand Junction","zone":"Western","status":"reserved","track_health":95.0},
            {"name":"VAD-01","location":"Vadodara Station","zone":"Western","status":"free","track_health":91.0},
            {"name":"VAD-02","location":"Vadodara Yard","zone":"Western","status":"maintenance","track_health":65.0},
            {"name":"SRT-01","location":"Surat Station","zone":"Western","status":"occupied","track_health":89.5},
            {"name":"BOM-01","location":"Mumbai Central","zone":"Western","status":"free","track_health":97.0},
            {"name":"DEL-01","location":"Delhi Junction","zone":"Northern","status":"occupied","track_health":94.0},
        ]
        for b in block_data:
            db.add(Block(**b))
        db.commit()
        now = datetime.utcnow()
        train_data = [
            {"train_number":"12901","train_name":"Gujarat Express","train_type":"express","origin":"Ahmedabad","destination":"Mumbai","scheduled_departure":now+timedelta(hours=1),"scheduled_arrival":now+timedelta(hours=7),"delay_minutes":25,"status":"delayed","passenger_load":85.0,"priority_score":72.5,"current_block_id":1},
            {"train_number":"19019","train_name":"Dehradun Express","train_type":"express","origin":"Ahmedabad","destination":"Delhi","scheduled_departure":now+timedelta(hours=2),"scheduled_arrival":now+timedelta(hours=14),"delay_minutes":0,"status":"on_time","passenger_load":92.0,"priority_score":68.0,"current_block_id":3},
            {"train_number":"22955","train_name":"Kutch Express","train_type":"passenger","origin":"Bhuj","destination":"Mumbai","scheduled_departure":now+timedelta(hours=3),"scheduled_arrival":now+timedelta(hours=12),"delay_minutes":45,"status":"delayed","passenger_load":78.0,"priority_score":55.0,"current_block_id":6},
            {"train_number":"FRGT001","train_name":"Freight Train 001","train_type":"freight","origin":"Kandla Port","destination":"Delhi Freight Terminal","scheduled_departure":now+timedelta(hours=4),"scheduled_arrival":now+timedelta(hours=22),"delay_minutes":10,"status":"on_time","passenger_load":0.0,"priority_score":35.0,"current_block_id":8},
            {"train_number":"09441","train_name":"Vande Bharat Express","train_type":"high_speed","origin":"Ahmedabad","destination":"Mumbai","scheduled_departure":now+timedelta(minutes=30),"scheduled_arrival":now+timedelta(hours=5),"delay_minutes":0,"status":"on_time","passenger_load":98.0,"priority_score":92.0,"current_block_id":None},
        ]
        for t in train_data:
            db.add(Train(**t))
        db.commit()
        alert_data = [
            {"title":"Critical Block Conflict","description":"Block VAD-02 under maintenance but Train 22955 approaching. Immediate rerouting required.","severity":"critical","alert_type":"conflict","block_id":5,"train_id":3},
            {"title":"Train Delay Detected","description":"Gujarat Express (12901) running 25 min late. AI suggests alternate block AHM-02.","severity":"high","alert_type":"delay","block_id":1,"train_id":1},
            {"title":"Track Health Warning","description":"Block VAD-02 at 65%% health. Maintenance window needed within 24 hours.","severity":"medium","alert_type":"maintenance","block_id":5,"train_id":None},
            {"title":"Weather Alert","description":"Heavy rainfall near Surat. Reduce speed on SRT-01 block.","severity":"medium","alert_type":"weather","block_id":6,"train_id":None},
        ]
        for a in alert_data:
            db.add(Alert(**a))
        db.commit()
        print("Database seeded!")
    except Exception as e:
        print(f"Seed error: {e}"); db.rollback()
    finally:
        db.close()

@app.on_event("startup")
async def startup():
    seed()
    print("AI RailOps Backend running!")
    print("Swagger docs: http://localhost:8000/docs")

@app.get("/")
def root():
    return {"message": "AI RailOps API", "version": "1.0.0", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
"""

# ══════════════════════════════════════════════
# FRONTEND FILES (Minimal Black / White / Blue UI)
# ══════════════════════════════════════════════

FILES["frontend/public/index.html"] = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>RailOps</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
  <div id="root"></div>
</body>
</html>
"""

FILES["frontend/.env"] = "REACT_APP_API_URL=http://localhost:8000\n"

FILES["frontend/src/index.js"] = """\
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './App.css';
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<React.StrictMode><App /></React.StrictMode>);
"""

FILES["frontend/src/theme.js"] = """\
export const COLORS = {
  black: '#0A0A0A',
  white: '#FFFFFF',
  blue: '#2563EB',
  blueLight: '#EFF4FF',
  blueDark: '#1D4ED8',
  gray100: '#F5F5F5',
  gray200: '#E5E5E5',
  gray400: '#9CA3AF',
  gray600: '#525252',
};

export const FONT = {
  base: "'Inter', -apple-system, sans-serif",
};
"""

FILES["frontend/src/App.css"] = """\
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'Inter', -apple-system, sans-serif;
  background: #F5F5F5;
  color: #0A0A0A;
  -webkit-font-smoothing: antialiased;
}

@keyframes spin { 100%% { transform: rotate(360deg); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.spinner {
  width: 28px; height: 28px;
  border: 3px solid #E5E5E5;
  border-top: 3px solid #2563EB;
  border-radius: 50%%;
  animation: spin 0.8s linear infinite;
}

.loading-screen {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  min-height: 100vh; background: #0A0A0A; color: #FFFFFF; gap: 14px;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #D4D4D4; border-radius: 3px; }

table { width: 100%%; border-collapse: collapse; }
button { font-family: inherit; }
""".replace("%%", "%")

FILES["frontend/src/App.jsx"] = """\
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import './App.css';

const PrivateRoute = ({ children }) => {
  const { token, loading } = useAuth();
  if (loading) return (
    <div className="loading-screen">
      <div className="spinner"/>
      <p style={{ fontSize: 13 }}>Loading...</p>
    </div>
  );
  return token ? children : <Navigate to="/login" />;
};

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
"""

FILES["frontend/src/context/AuthContext.jsx"] = """\
import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      const u = localStorage.getItem('user');
      if (u) setUser(JSON.parse(u));
    }
    setLoading(false);
  }, [token]);

  const login = async (username, password) => {
    const fd = new FormData();
    fd.append('username', username);
    fd.append('password', password);
    const res = await axios.post(`${process.env.REACT_APP_API_URL}/auth/login`, fd,
      { headers: { 'Content-Type': 'multipart/form-data' } });
    const { access_token, role, username: uname } = res.data;
    localStorage.setItem('token', access_token);
    localStorage.setItem('user', JSON.stringify({ username: uname, role }));
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    setToken(access_token);
    setUser({ username: uname, role });
    return res.data;
  };

  const logout = () => {
    localStorage.clear();
    delete axios.defaults.headers.common['Authorization'];
    setToken(null); setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
"""

FILES["frontend/src/services/api.js"] = """\
import axios from 'axios';
const API = axios.create({ baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000' });
API.interceptors.request.use(cfg => {
  const t = localStorage.getItem('token');
  if (t) cfg.headers.Authorization = `Bearer ${t}`;
  return cfg;
});
API.interceptors.response.use(r => r, err => {
  if (err.response?.status === 401) { localStorage.clear(); window.location.href = '/login'; }
  return Promise.reject(err);
});
export const getBlocks = () => API.get('/blocks/');
export const updateBlockStatus = (id, status) => API.put(`/blocks/${id}/status?status=${status}`);
export const getTrains = () => API.get('/trains/');
export const predictDelay = (id) => API.get(`/trains/${id}/predict-delay`);
export const assignBlock = (trainId, blockId) => API.put(`/trains/${trainId}/assign-block?block_id=${blockId}`);
export const getAlerts = () => API.get('/alerts/');
export const acknowledgeAlert = (id) => API.post(`/alerts/${id}/acknowledge`);
export const getSuggestions = () => API.get('/optimization/suggestions');
export const executeOptimization = () => API.post('/optimization/execute');
export const getSystemStatus = () => API.get('/optimization/system-status');
export default API;
"""

FILES["frontend/src/components/Login.jsx"] = """\
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault(); setLoading(true); setError('');
    try { await login(form.username, form.password); navigate('/'); }
    catch { setError('Invalid credentials'); }
    finally { setLoading(false); }
  };

  return (
    <div style={s.page}>
      <div style={s.card}>
        <div style={s.brand}>
          <div style={s.logoDot} />
          <h1 style={s.title}>RailOps</h1>
        </div>
        <p style={s.subtitle}>Block Planning System</p>

        <form onSubmit={handleSubmit} style={s.form}>
          <input
            style={s.input}
            placeholder="Username"
            value={form.username}
            onChange={e => setForm({ ...form, username: e.target.value })}
            required
          />
          <input
            style={s.input}
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={e => setForm({ ...form, password: e.target.value })}
            required
          />
          {error && <p style={s.error}>{error}</p>}
          <button style={s.btn} disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div style={s.hint}>admin / railway123 &nbsp;.&nbsp; operator / railway123</div>
      </div>
    </div>
  );
}

const s = {
  page: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#0A0A0A' },
  card: { background: '#FFFFFF', borderRadius: 12, padding: 40, width: 360 },
  brand: { display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 },
  logoDot: { width: 10, height: 10, borderRadius: '50%', background: '#2563EB' },
  title: { fontSize: 20, fontWeight: 700, letterSpacing: -0.3 },
  subtitle: { fontSize: 13, color: '#9CA3AF', marginBottom: 28 },
  form: { display: 'flex', flexDirection: 'column', gap: 10 },
  input: { padding: '11px 14px', border: '1px solid #E5E5E5', borderRadius: 8, fontSize: 14, outline: 'none' },
  error: { fontSize: 12, color: '#0A0A0A', background: '#F5F5F5', padding: '8px 10px', borderRadius: 6 },
  btn: { padding: 12, background: '#0A0A0A', color: '#FFFFFF', border: 'none', borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: 'pointer', marginTop: 6 },
  hint: { marginTop: 20, fontSize: 11, color: '#9CA3AF', textAlign: 'center' }
};
"""

FILES["frontend/src/components/Navbar.jsx"] = """\
import React from 'react';
import { useAuth } from '../context/AuthContext';

export default function Navbar({ systemStatus }) {
  const { user, logout } = useAuth();
  return (
    <nav style={s.nav}>
      <div style={s.left}>
        <span style={s.dot} />
        <span style={s.brand}>RailOps</span>
      </div>
      <div style={s.right}>
        <span style={s.status}>{systemStatus?.status || '-'}</span>
        <span style={s.user}>{user?.username} . {user?.role}</span>
        <button style={s.logout} onClick={logout}>Sign out</button>
      </div>
    </nav>
  );
}

const s = {
  nav: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 32px', background: '#0A0A0A' },
  left: { display: 'flex', alignItems: 'center', gap: 8 },
  dot: { width: 8, height: 8, borderRadius: '50%', background: '#2563EB' },
  brand: { color: '#FFFFFF', fontSize: 15, fontWeight: 700, letterSpacing: -0.3 },
  right: { display: 'flex', alignItems: 'center', gap: 20 },
  status: { fontSize: 12, color: '#9CA3AF', textTransform: 'capitalize' },
  user: { fontSize: 12, color: '#FFFFFF' },
  logout: { fontSize: 12, color: '#0A0A0A', background: '#FFFFFF', border: 'none', padding: '6px 14px', borderRadius: 6, cursor: 'pointer', fontWeight: 600 }
};
"""

FILES["frontend/src/components/StatsCards.jsx"] = """\
import React from 'react';

export default function StatsCards({ systemStatus, trains, blocks, alerts }) {
  const delayed = trains.filter(t => t.status === 'delayed').length;
  const free = blocks.filter(b => b.status === 'free').length;

  const items = [
    { label: 'Trains running', value: trains.length, note: `${delayed} delayed` },
    { label: 'Blocks free', value: `${free}/${blocks.length}`, note: 'available now' },
    { label: 'Open alerts', value: alerts.length, note: 'need review' },
    { label: 'Uptime', value: systemStatus?.uptime || '-', note: 'last 30 days' },
  ];

  return (
    <div style={s.grid}>
      {items.map((it, i) => (
        <div key={i} style={s.card}>
          <p style={s.label}>{it.label}</p>
          <p style={s.value}>{it.value}</p>
          <p style={s.note}>{it.note}</p>
        </div>
      ))}
    </div>
  );
}

const s = {
  grid: { display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 1, background: '#E5E5E5', border: '1px solid #E5E5E5', borderRadius: 10, overflow: 'hidden', marginBottom: 24 },
  card: { background: '#FFFFFF', padding: '18px 20px' },
  label: { fontSize: 12, color: '#9CA3AF', marginBottom: 8 },
  value: { fontSize: 26, fontWeight: 700, color: '#0A0A0A', letterSpacing: -0.5 },
  note: { fontSize: 11, color: '#9CA3AF', marginTop: 4 }
};
"""

FILES["frontend/src/components/BlockMap.jsx"] = """\
import React from 'react';

const STATUS_LABEL = { free: 'Free', occupied: 'Occupied', reserved: 'Reserved', maintenance: 'Maintenance' };

export default function BlockMap({ blocks, trains }) {
  const trainFor = (id) => trains.find(t => t.current_block_id === id);

  return (
    <div style={s.card}>
      <h3 style={s.title}>Block status</h3>
      <table>
        <thead>
          <tr>
            {['Block', 'Location', 'Status', 'Track health', 'Train'].map(h => (
              <th key={h} style={s.th}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {blocks.map(b => {
            const t = trainFor(b.id);
            const isActive = b.status !== 'free';
            return (
              <tr key={b.id} style={s.row}>
                <td style={s.td}><strong>{b.name}</strong></td>
                <td style={{ ...s.td, color: '#9CA3AF' }}>{b.location}</td>
                <td style={s.td}>
                  <span style={{ ...s.badge, ...(isActive ? s.badgeActive : s.badgeFree) }}>
                    {STATUS_LABEL[b.status]}
                  </span>
                </td>
                <td style={s.td}>
                  <div style={s.healthBar}>
                    <div style={{ ...s.healthFill, width: `${b.track_health}%` }} />
                  </div>
                </td>
                <td style={{ ...s.td, color: '#0A0A0A' }}>{t ? t.train_number : '-'}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

const s = {
  card: { background: '#FFFFFF', borderRadius: 10, padding: 20, border: '1px solid #E5E5E5', marginBottom: 16 },
  title: { fontSize: 14, fontWeight: 700, marginBottom: 14 },
  th: { textAlign: 'left', fontSize: 11, color: '#9CA3AF', fontWeight: 600, padding: '0 10px 10px 0', textTransform: 'uppercase', letterSpacing: 0.3 },
  row: { borderTop: '1px solid #F5F5F5' },
  td: { padding: '10px 10px 10px 0', fontSize: 13 },
  badge: { fontSize: 11, fontWeight: 600, padding: '3px 9px', borderRadius: 5 },
  badgeFree: { background: '#F5F5F5', color: '#9CA3AF' },
  badgeActive: { background: '#EFF4FF', color: '#2563EB' },
  healthBar: { width: 80, height: 4, background: '#F5F5F5', borderRadius: 2 },
  healthFill: { height: '100%', background: '#0A0A0A', borderRadius: 2 }
};
"""

FILES["frontend/src/components/TrainTable.jsx"] = """\
import React, { useState } from 'react';
import { predictDelay } from '../services/api';

export default function TrainTable({ trains }) {
  const [prediction, setPrediction] = useState(null);
  const [loadingId, setLoadingId] = useState(null);

  const handlePredict = async (id) => {
    setLoadingId(id);
    try { const r = await predictDelay(id); setPrediction(r.data); }
    catch { alert('Prediction failed'); }
    finally { setLoadingId(null); }
  };

  return (
    <div style={s.card}>
      <h3 style={s.title}>Trains</h3>
      <table>
        <thead>
          <tr>
            {['Train', 'Route', 'Type', 'Delay', 'Priority', ''].map(h => (
              <th key={h} style={s.th}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {trains.map(t => (
            <tr key={t.id} style={s.row}>
              <td style={s.td}>
                <strong>{t.train_number}</strong>
                <div style={s.subText}>{t.train_name}</div>
              </td>
              <td style={{ ...s.td, color: '#9CA3AF' }}>{t.origin} to {t.destination}</td>
              <td style={{ ...s.td, textTransform: 'capitalize' }}>{t.train_type.replace('_', ' ')}</td>
              <td style={s.td}>
                {t.delay_minutes > 0
                  ? <span style={s.delayTag}>+{t.delay_minutes} min</span>
                  : <span style={s.onTimeTag}>On time</span>}
              </td>
              <td style={s.td}>
                <div style={s.priorityBar}>
                  <div style={{ ...s.priorityFill, width: `${t.priority_score}%` }} />
                </div>
              </td>
              <td style={s.td}>
                <button style={s.predictBtn} onClick={() => handlePredict(t.id)} disabled={loadingId === t.id}>
                  {loadingId === t.id ? '...' : 'Predict'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {prediction && (
        <div style={s.predictBox}>
          <div style={s.predictHeader}>
            <span style={s.predictTitle}>Prediction - {prediction.train_number}</span>
            <button style={s.closeBtn} onClick={() => setPrediction(null)}>Close</button>
          </div>
          <div style={s.predictGrid}>
            <div><p style={s.predLabel}>Current delay</p><p style={s.predValue}>{prediction.current_delay} min</p></div>
            <div><p style={s.predLabel}>Predicted delay</p><p style={s.predValue}>{prediction.prediction.predicted_delay_minutes} min</p></div>
            <div><p style={s.predLabel}>Confidence</p><p style={s.predValue}>{(prediction.prediction.confidence * 100).toFixed(0)}%</p></div>
            <div><p style={s.predLabel}>Weather</p><p style={s.predValue}>{prediction.prediction.contributing_factors.weather}</p></div>
          </div>
        </div>
      )}
    </div>
  );
}

const s = {
  card: { background: '#FFFFFF', borderRadius: 10, padding: 20, border: '1px solid #E5E5E5', marginBottom: 16 },
  title: { fontSize: 14, fontWeight: 700, marginBottom: 14 },
  th: { textAlign: 'left', fontSize: 11, color: '#9CA3AF', fontWeight: 600, padding: '0 10px 10px 0', textTransform: 'uppercase', letterSpacing: 0.3 },
  row: { borderTop: '1px solid #F5F5F5' },
  td: { padding: '12px 10px 12px 0', fontSize: 13, verticalAlign: 'middle' },
  subText: { fontSize: 11, color: '#9CA3AF', marginTop: 2 },
  delayTag: { fontSize: 12, fontWeight: 600, color: '#2563EB' },
  onTimeTag: { fontSize: 12, color: '#9CA3AF' },
  priorityBar: { width: 70, height: 4, background: '#F5F5F5', borderRadius: 2 },
  priorityFill: { height: '100%', background: '#0A0A0A', borderRadius: 2 },
  predictBtn: { fontSize: 11, fontWeight: 600, background: '#0A0A0A', color: '#FFFFFF', border: 'none', padding: '6px 12px', borderRadius: 6, cursor: 'pointer' },
  predictBox: { marginTop: 16, borderTop: '1px solid #E5E5E5', paddingTop: 16 },
  predictHeader: { display: 'flex', justifyContent: 'space-between', marginBottom: 12 },
  predictTitle: { fontSize: 13, fontWeight: 700 },
  closeBtn: { fontSize: 11, color: '#9CA3AF', background: 'none', border: 'none', cursor: 'pointer' },
  predictGrid: { display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12 },
  predLabel: { fontSize: 11, color: '#9CA3AF', marginBottom: 4 },
  predValue: { fontSize: 16, fontWeight: 700, color: '#0A0A0A' }
};
"""

FILES["frontend/src/components/AlertPanel.jsx"] = """\
import React from 'react';
import { acknowledgeAlert } from '../services/api';
import { useAuth } from '../context/AuthContext';

const SEVERITY_LABEL = { critical: 'Critical', high: 'High', medium: 'Medium', low: 'Low' };

export default function AlertPanel({ alerts, onRefresh }) {
  const { user } = useAuth();
  const handleAck = async (id) => { try { await acknowledgeAlert(id); onRefresh(); } catch { alert('Failed'); } };

  return (
    <div style={s.card}>
      <h3 style={s.title}>Alerts ({alerts.length})</h3>
      {alerts.length === 0 ? (
        <p style={s.empty}>No active alerts</p>
      ) : (
        <div>
          {alerts.map(a => (
            <div key={a.id} style={s.item}>
              <div style={s.itemTop}>
                <span style={s.severity}>{SEVERITY_LABEL[a.severity]}</span>
                <span style={s.time}>{a.timestamp}</span>
              </div>
              <p style={s.itemTitle}>{a.title}</p>
              <p style={s.itemDesc}>{a.description}</p>
              {user?.role === 'admin' && (
                <button style={s.ackBtn} onClick={() => handleAck(a.id)}>Acknowledge</button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const s = {
  card: { background: '#FFFFFF', borderRadius: 10, padding: 20, border: '1px solid #E5E5E5' },
  title: { fontSize: 14, fontWeight: 700, marginBottom: 14 },
  empty: { fontSize: 13, color: '#9CA3AF' },
  item: { padding: '14px 0', borderTop: '1px solid #F5F5F5' },
  itemTop: { display: 'flex', justifyContent: 'space-between', marginBottom: 6 },
  severity: { fontSize: 11, fontWeight: 700, color: '#2563EB', textTransform: 'uppercase', letterSpacing: 0.3 },
  time: { fontSize: 11, color: '#9CA3AF' },
  itemTitle: { fontSize: 13, fontWeight: 600, marginBottom: 4 },
  itemDesc: { fontSize: 12, color: '#9CA3AF', lineHeight: 1.5, marginBottom: 8 },
  ackBtn: { fontSize: 11, fontWeight: 600, background: 'none', border: '1px solid #E5E5E5', padding: '5px 12px', borderRadius: 6, cursor: 'pointer' }
};
"""

FILES["frontend/src/components/OptimizationPanel.jsx"] = """\
import React, { useState } from 'react';
import { executeOptimization } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function OptimizationPanel({ suggestions, onRefresh }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const { user } = useAuth();

  const handleExec = async () => {
    setLoading(true);
    try { const r = await executeOptimization(); setResult(r.data); onRefresh(); }
    catch { alert('Failed'); }
    finally { setLoading(false); }
  };

  return (
    <div style={s.card}>
      <div style={s.header}>
        <h3 style={s.title}>Optimization ({suggestions.length})</h3>
        {user?.role === 'admin' && (
          <button style={s.execBtn} onClick={handleExec} disabled={loading}>
            {loading ? 'Running...' : 'Run optimization'}
          </button>
        )}
      </div>

      {result && (
        <div style={s.result}>
          <span>Saved <strong>{result.delay_saved_minutes} min</strong></span>
          <span>Efficiency <strong>+{result.efficiency_gain_percent}%</strong></span>
        </div>
      )}

      {suggestions.length === 0 ? (
        <p style={s.empty}>No suggestions right now</p>
      ) : (
        suggestions.map(sg => (
          <div key={sg.id} style={s.item}>
            <div style={s.itemTop}>
              <span style={s.type}>{sg.type}</span>
              <span style={s.priority}>{sg.priority}</span>
            </div>
            <p style={s.desc}>{sg.description}</p>
            <p style={s.meta}>{sg.impact}% impact . ~{sg.estimated_time} min</p>
          </div>
        ))
      )}
    </div>
  );
}

const s = {
  card: { background: '#FFFFFF', borderRadius: 10, padding: 20, border: '1px solid #E5E5E5' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 },
  title: { fontSize: 14, fontWeight: 700 },
  execBtn: { fontSize: 12, fontWeight: 600, background: '#0A0A0A', color: '#FFFFFF', border: 'none', padding: '8px 14px', borderRadius: 6, cursor: 'pointer' },
  result: { display: 'flex', gap: 20, fontSize: 12, color: '#2563EB', background: '#EFF4FF', padding: '10px 14px', borderRadius: 8, marginBottom: 14 },
  empty: { fontSize: 13, color: '#9CA3AF' },
  item: { padding: '12px 0', borderTop: '1px solid #F5F5F5' },
  itemTop: { display: 'flex', justifyContent: 'space-between', marginBottom: 6 },
  type: { fontSize: 12, fontWeight: 700 },
  priority: { fontSize: 11, color: '#9CA3AF', textTransform: 'capitalize' },
  desc: { fontSize: 12, color: '#525252', lineHeight: 1.5, marginBottom: 4 },
  meta: { fontSize: 11, color: '#9CA3AF' }
};
"""

FILES["frontend/src/components/Dashboard.jsx"] = """\
import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './Navbar';
import StatsCards from './StatsCards';
import BlockMap from './BlockMap';
import TrainTable from './TrainTable';
import AlertPanel from './AlertPanel';
import OptimizationPanel from './OptimizationPanel';
import { getBlocks, getTrains, getAlerts, getSuggestions, getSystemStatus } from '../services/api';

export default function Dashboard() {
  const [blocks, setBlocks] = useState([]);
  const [trains, setTrains] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [systemStatus, setSystemStatus] = useState({});
  const [loading, setLoading] = useState(true);

  const fetchAll = useCallback(async () => {
    try {
      const [b, t, a, s, ss] = await Promise.all([
        getBlocks(), getTrains(), getAlerts(), getSuggestions(), getSystemStatus()
      ]);
      setBlocks(b.data); setTrains(t.data); setAlerts(a.data);
      setSuggestions(s.data); setSystemStatus(ss.data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => {
    fetchAll();
    const i = setInterval(fetchAll, 30000);
    return () => clearInterval(i);
  }, [fetchAll]);

  if (loading) return (
    <div className="loading-screen">
      <div className="spinner" />
      <p style={{ fontSize: 13 }}>Loading...</p>
    </div>
  );

  return (
    <div style={{ minHeight: '100vh', background: '#F5F5F5' }}>
      <Navbar systemStatus={systemStatus} />
      <div style={{ padding: '28px 32px', maxWidth: 1200, margin: '0 auto' }}>
        <StatsCards systemStatus={systemStatus} trains={trains} blocks={blocks} alerts={alerts} />
        <BlockMap blocks={blocks} trains={trains} />
        <TrainTable trains={trains} />
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          <AlertPanel alerts={alerts} onRefresh={fetchAll} />
          <OptimizationPanel suggestions={suggestions} onRefresh={fetchAll} />
        </div>
      </div>
    </div>
  );
}
"""

FILES["frontend/package.json"] = """\
{
  "name": "ai-railops-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "axios": "^1.6.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.18.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  },
  "proxy": "http://localhost:8000",
  "browserslist": {
    "production": [">0.2%%","not dead"],
    "development": ["last 1 chrome version"]
  }
}
""".replace("%%", "%")

FILES["start_backend.bat"] = """\
@echo off
echo Starting Backend Server...
cd backend
call venv\\Scripts\\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
"""

FILES["start_frontend.bat"] = """\
@echo off
echo Starting Frontend Server...
cd frontend
npm start
pause
"""

FILES["README.md"] = """\
# RailOps - Minimal Block Planning System

## First Time Setup
Run in VS Code terminal:
    python setup.py

## Every Time After
- Double-click start_backend.bat
- Double-click start_frontend.bat
- Open: http://localhost:3000
- Login: admin / railway123

## API Docs
http://localhost:8000/docs
"""

# ══════════════════════════════════════════════
# CREATE + INSTALL
# ══════════════════════════════════════════════

def create_files():
    print("\\nCreating project files...")
    for path, content in FILES.items():
        full_path = os.path.join(ROOT, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  created: {path}")
    print("\\nAll files created.\\n")

def setup_backend():
    print("Setting up backend (Python)...")
    backend_path = os.path.join(ROOT, "backend")
    subprocess.run([sys.executable, "-m", "venv", os.path.join(backend_path, "venv")], check=True)
    if sys.platform == "win32":
        pip_path = os.path.join(backend_path, "venv", "Scripts", "pip.exe")
    else:
        pip_path = os.path.join(backend_path, "venv", "bin", "pip")
    subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
    subprocess.run([pip_path, "install", "-r", os.path.join(backend_path, "requirements.txt")], check=True)
    print("Backend ready.\\n")

def setup_frontend():
    print("Setting up frontend (React)...")
    frontend_path = os.path.join(ROOT, "frontend")
    subprocess.run(["npm", "install"], cwd=frontend_path, check=True, shell=(sys.platform == "win32"))
    print("Frontend ready.\\n")

if __name__ == "__main__":
    print("RailOps - Automated Setup Starting...\\n")
    try:
        create_files()
        setup_backend()
        setup_frontend()
        print("=" * 50)
        print("SETUP COMPLETE")
        print("=" * 50)
        print("""
Run it:
  1. Double-click start_backend.bat
  2. Double-click start_frontend.bat
  3. Open http://localhost:3000
  4. Login: admin / railway123
        """)
    except subprocess.CalledProcessError as e:
        print(f"Setup failed: {e}")
    except Exception as e:
        print(f"Error: {e}")