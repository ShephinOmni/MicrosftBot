pass
# from fastapi import APIRouter, HTTPException
# from sqlalchemy.orm import Session
# from . import models, schemas, database

# router = APIRouter()

# @router.post("/participants/", response_model=schemas.Participant)
# def create_participant(participant: schemas.ParticipantCreate, db: Session = database.SessionLocal()):
#     db_participant = models.Participant(name=participant.name)
#     db.add(db_participant)
#     db.commit()
#     db.refresh(db_participant)
#     return db_participant

# @router.get("/participants/", response_model=list[schemas.Participant])
# def read_participants(skip: int = 0, limit: int = 10, db: Session = database.SessionLocal()):
#     participants = db.query(models.Participant).offset(skip).limit(limit).all()
#     return participants
