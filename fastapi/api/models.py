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
    
    search_content = relationship("SearchContent", back_populates="teaching_plan", uselist=False)

class SearchContent(Base):
    __tablename__ = "search_contents"
    
    teaching_plan_id = Column(Integer, ForeignKey("teaching_plan.id"), primary_key=True)
    content = Column(Text, nullable=False)
    similarity_score = Column(Float)
    
    teaching_plan = relationship("TeachingPlan", back_populates="search_content")
    
class Admin(Base):
    __tablename__ = 'admin'
    admin_name = Column(String, primary_key=True)
    hashed_password=Column(String, unique=True)
    