from pydantic import BaseModel

class AdminSchema(BaseModel):
    admin_name: str
    hashed_password: str  # 假設密碼已經加密

    class Config:
        orm_mode = True  # 讓 SQLAlchemy Model 可以轉換為 Pydantic