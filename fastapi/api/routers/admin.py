from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Admin
from ..auth import get_current_admin

router = APIRouter()

@router.get("/admin")
async def get_admin_page(current_admin: Admin = Depends(get_current_admin)):
    return {"admin_name": current_admin.admin_name}

@router.post("/admin")
async def create_admin(admin: Admin, db: Session = Depends(get_db)):
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin