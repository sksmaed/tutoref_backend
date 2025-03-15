from sqlalchemy import Column, Integer, Float, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class TeachingPlan(Base):
    __tablename__ = 'teaching_plan'
    id = Column(Integer, primary_key=True, autoincrement=True) 
    tp_name = Column(String)
    writer_name = Column(String)
    team = Column(String)
    semester = Column(String)
    category = Column(String)
    grade = Column(String)
    duration = Column(Integer)
    staffing = Column(String)
    venue = Column(String)
    objectives = Column(String)
    outline = Column(String)
    sheet_docx = Column(String)
    sheet_pdf = Column(String)
    slide_pptx = Column(String)
    slide_pdf = Column(String)
    is_open = Column(Integer)


class Announcement(Base):
    __tablename__ = 'announcement'
    id = Column(Integer, primary_key=True, autoincrement=True) 
    title = Column(String)
    content = Column(String)
    writer_name = Column(String)
    created_at = Column(String)
    
class Admin(Base):
    __tablename__ = 'admin'
    admin_name = Column(String, primary_key=True)
    hashed_password=Column(String, unique=True)
    
