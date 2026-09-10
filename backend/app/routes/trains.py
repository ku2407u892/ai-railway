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
