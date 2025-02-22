import asyncio
from ..utils import schemas
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..utils.doc_preprocessor import TeachingPlanProcessor
from .. import models
import shutil
import os

router = APIRouter()
processor = TeachingPlanProcessor()

@router.post("/api/submit-plans")
async def upload_teaching_plan(
    request: Request,
    plans: List[schemas.TeachingPlan],  
    db: Session = Depends(get_db)
):
    """接收 JSON 格式的教案資料並存入 PostgreSQL 和 Elasticsearch"""

    try:
        new_plans = []
        es_docs = []

        for plan_data in plans:
            # 轉換為 SQLAlchemy 模型
            teaching_plan = models.TeachingPlan(**plan_data.dict())
            db.add(teaching_plan)
            db.flush()  # 取得新 ID

            # 準備要存入 Elasticsearch 的資料
            es_doc = {
                "semester": plan_data.semester,
                "category": plan_data.category,
                "grade": plan_data.grade,
                "duration": plan_data.duration,
                "writer_name": plan_data.writer_name,
                "objectives": plan_data.objectives,
                "outline": plan_data.outline,
            }
            es_docs.append({"id": teaching_plan.id, "doc": es_doc})

            new_plans.append(teaching_plan)

        # 批量寫入 Elasticsearch
        for es_data in es_docs:
            await request.app.state.es_client.index_teaching_plan(
                teaching_plan_id=str(es_data["id"]),
                doc=es_data["doc"]
            )

        db.commit()

        return {"message": "Teaching plans uploaded successfully"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/upload-file")
async def upload_folder(
    request: Request,
    files: List[UploadFile] = File(...)
):
    """批量上傳並處理教案 PDF"""
            
    # 創建臨時目錄
    temp_dir = "temp_files"
    os.makedirs(temp_dir, exist_ok=True)
    
    parsed_plans = []
    temp_paths = []
    
    try:
        # 儲存所有檔案
        for file in files:
            temp_path = os.path.join(temp_dir, file.filename)
            temp_paths.append(temp_path)
            
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        
        # 非同步處理所有檔案
        async def process_file(file_path: str):
            try:
                # 提取文字
                text = processor.extract_pdf_text(file_path)
                
                # 解析教案內容
                basic_info = processor.parse_teaching_plan(text)
                basic_info.update({
                    "sheet_docx": "",
                    "sheet_pdf": "",
                    "slide_pptx": "",
                    "slide_pdf": ""
                })
                
                return basic_info
                
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                return None
        
        # 創建處理任務
        tasks = [process_file(path) for path in temp_paths]
        
        # 等待所有任務完成
        results = await asyncio.gather(*tasks)
        
        # 過濾掉處理失敗的結果
        parsed_plans = [plan for plan in results if plan is not None]
        
        # 為每個計畫生成臨時ID
        for i, plan in enumerate(parsed_plans):
            plan["id"] = f"temp_{i}"
        
        return parsed_plans
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # 清理臨時檔案
        for path in temp_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"Error removing temporary file {path}: {str(e)}")
        
        # 如果臨時目錄為空，刪除它
        try:
            if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                os.rmdir(temp_dir)
        except Exception as e:
            print(f"Error removing temporary directory: {str(e)}")

# 配置FastAPI應用
def configure(app):
    app.include_router(router)
