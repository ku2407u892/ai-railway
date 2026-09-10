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
