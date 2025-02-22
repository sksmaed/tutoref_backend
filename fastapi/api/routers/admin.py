from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Admin
from ..auth import get_current_admin

router = APIRouter()

@router.get("/admin")
async def get_admin_page(current_admin: Admin = Depends(get_current_admin)):
    return {"message": f"Welcome to admin page"}