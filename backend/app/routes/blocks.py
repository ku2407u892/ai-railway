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
