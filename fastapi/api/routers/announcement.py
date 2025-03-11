from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Announcement

router = APIRouter()

@router.get("/api/announcement")
async def get_announcement(
    db: Session = Depends(get_db)
):
    return db.query(Announcement).all()

@router.post("/api/announcement")
async def create_announcement(
    request: Request,
    announcement: Announcement,
    db: Session = Depends(get_db)
):
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement

@router.put("/api/announcement/{announcement_id}")
async def update_announcement(
    announcement_id: int,
    request: Request,
    announcement: Announcement,
    db: Session = Depends(get_db)
):
    db.query(Announcement).filter(Announcement.id == announcement_id).update({
        "title": announcement.title,
        "content": announcement.content,
        "writer_name": announcement.writer_name,
        "created_at": announcement.created_at
    })
    db.commit()
    return announcement

@router.delete("/api/announcement/{announcement_id}")
async def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db)
):
    db.query(Announcement).filter(Announcement.id == announcement_id).delete()
    db.commit()
    return {"message": "Announcement deleted successfully"}
