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
