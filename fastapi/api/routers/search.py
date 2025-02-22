import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from ..utils.privacy import get_team_from_hash
from ..database import get_db
from ..models import TeachingPlan
from pydantic import BaseModel

router = APIRouter()

class SearchFilters(BaseModel):
    team: List[str] = []
    semester: List[str] = []
    category: List[str] = []
    grade: List[str] = []
    duration: List[int] = []
    keyword: Optional[str] = None
    writer_name: Optional[str] = None
    teamHash: Optional[str] = None


@router.post("/api/search")
async def search_teaching_plans(
    request: Request,
    filters: SearchFilters,
    db: Session = Depends(get_db)
):
    real_team = None
    if filters.teamHash:
        real_team = get_team_from_hash(filters.teamHash)
        if not real_team:
            raise HTTPException(status_code=403, detail="無效的 team 參數")

    try:
        # 準備過濾條件
        query = filters.keyword if filters.keyword else ""

        filter_params = {}
        for field in ["semester", "category", "grade", "duration", "team"]:
            if values := getattr(filters, field):
                if values:  # 確保列表不為空
                    filter_params[field] = values

        # 執行 ES 搜尋
        print(filter_params)
        es_results = await request.app.state.es_client.search(
            query=query,
            writer_name=filters.writer_name,  # 傳遞作者名稱
            filters=filter_params if filter_params else None
        )

        # 處理搜尋結果
        result_ids = []
        scores = {}
        print(es_results)
        if es_results:
            for hit in es_results["hits"]:
                if hit["_score"] > 0.7:
                    result_id = int(hit["_id"].split("_")[0])
                    result_ids.append(result_id)
                    scores[result_id] = hit["_score"]

        # 從資料庫獲取完整資料
        if result_ids:
            query = db.query(TeachingPlan).filter(TeachingPlan.id.in_(list(set(result_ids))))

            # 根據是否有 team 限制篩選
            if real_team:
                query = query.filter(TeachingPlan.team == real_team)
            else:
                query = query.filter(TeachingPlan.is_open == True)

            teaching_plans = query.all()
            print(query)

            return {
                "status": "success",
                "data": teaching_plans,
                "count": len(teaching_plans),
                "total_hits": es_results["total"]["value"]
            }

        return {
            "status": "success",
            "data": [],
            "count": 0,
            "total_hits": 0
        }

    except Exception as e:
        logging.error(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"搜尋過程發生錯誤: {str(e)}"
        )