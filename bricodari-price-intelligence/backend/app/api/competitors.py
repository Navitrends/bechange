from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Competitor
from app.schemas import CompetitorCreate, CompetitorOut

router = APIRouter()


@router.get("", response_model=list[CompetitorOut])
def list_competitors(db: Session = Depends(get_db)):
    return db.query(Competitor).order_by(Competitor.name).all()


@router.post("", response_model=CompetitorOut)
def create_competitor(payload: CompetitorCreate, db: Session = Depends(get_db)):
    existing = db.query(Competitor).filter(Competitor.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Concurrent déjà existant")
    competitor = Competitor(**payload.model_dump())
    db.add(competitor)
    db.commit()
    db.refresh(competitor)
    return competitor


@router.delete("/{competitor_id}")
def delete_competitor(competitor_id: int, db: Session = Depends(get_db)):
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Concurrent introuvable")
    db.delete(competitor)
    db.commit()
    return {"ok": True}
