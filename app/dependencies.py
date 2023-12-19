from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
pass

# def validate_participant(participant_id: int, db: Session):
#     # Example utility function
#    pass 
