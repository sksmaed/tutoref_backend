from pydantic import BaseModel
from typing import Optional

class TeachingPlan(BaseModel):
    semester: str
    category: str
    grade: str
    duration: int
    writer_name: str
    objectives: str
    outline: str
    staffing: Optional[str] = None
    venue: Optional[str] = None
    tp_name: Optional[str] = None
    team: Optional[str] = None

    # 新增文件欄位（這四個欄位是用來儲存文件名稱或URL）
    sheet_docx: Optional[str] = None
    sheet_pdf: Optional[str] = None
    slide_pptx: Optional[str] = None
    slide_pdf: Optional[str] = None

    class Config:
        orm_mode = True  # 讓 Pydantic 可以解析 SQLAlchemy 物件