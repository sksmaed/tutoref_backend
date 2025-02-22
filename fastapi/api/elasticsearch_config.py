from elasticsearch import AsyncElasticsearch
import logging
from typing import Dict, List, Optional
from .utils.doc_preprocessor import TeachingPlanProcessor

processor = TeachingPlanProcessor()

class ESClient:
    def __init__(self, elasticsearch_url: str):
        self.client = AsyncElasticsearch([elasticsearch_url])
        self.index_name = "teaching_plans"
        
    async def init_index(self):
        """初始化索引配置"""
        settings = {
            "analysis": {
                "analyzer": {
                    "custom_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "stop"]
                    }
                }
            }
        }
        
        mappings = {
            "properties": {
                "objectives": {"type": "text", "analyzer": "custom_analyzer"},
                "outline": {"type": "text", "analyzer": "custom_analyzer"},
                "content": {"type": "text", "analyzer": "custom_analyzer"}
            }
        }

        index_exists = await self.client.indices.exists(index=self.index_name)
        if not index_exists:
            await self.client.indices.create(
                index=self.index_name,
                settings=settings,
                mappings=mappings
            )
            logging.info(f"Created index {self.index_name}")

    async def index_teaching_plan(self, teaching_plan_id: str, doc: Dict):
        """
        索引教案文檔
        :param teaching_plan_id: 教案ID
        :param doc: 包含 objectives, outline 和 content 的文檔
        """
        try:
            await self.client.index(
                index=self.index_name,
                id=teaching_plan_id,
                document=doc
            )
            logging.info(f"Indexed teaching plan {teaching_plan_id}")
        except Exception as e:
            logging.error(f"Error indexing teaching plan: {str(e)}")
            raise

    async def search(self, query: str, writer_name: Optional[str] = None, filters: Optional[Dict] = None, top_k: int = 50) -> List[Dict]:
        """
        搜尋教案
        :param query: 搜尋關鍵字
        :param filters: 過濾條件
        :param top_k: 返回的結果數量
        :return: 符合條件的文檔列表
        """
        
        must_clauses = []
        
        # 主要關鍵字搜尋
        if query.strip():
            must_clauses.append({
                "multi_match": {
                    "query": query,
                    "fields": ["objectives", "outline"],
                    "type": "best_fields",
                    "operator": "or"
                }
            })

        # 搜尋作者名稱（writer_name）
        if writer_name and writer_name.strip():
            must_clauses.append({
                "wildcard": {
                    "writer_name": {
                        "value": f"*{writer_name}*",  # 允許部分匹配
                        "case_insensitive": True  # 不區分大小寫
                    }
                }
            })

        # 如果沒有關鍵字，也沒有作者名稱，就回傳所有資料
        if not must_clauses:
            must_clauses.append({"match_all": {}})

        search_body = {
            "query": {
                "bool": {
                    "must": must_clauses,
                    "filter": []
                }
            },
            "size": top_k
        }

        # 過濾條件
        if filters:
            for field, value in filters.items():
                if value:
                    if isinstance(value, list):
                        search_body["query"]["bool"]["filter"].append(
                            {"terms": {field: value}}
                        )
                    else:
                        search_body["query"]["bool"]["filter"].append(
                            {"term": {field: value}}
                        )

        print(search_body)
        try:
            response = await self.client.search(
                index=self.index_name,
                body=search_body
            )
            hits = response["hits"]
            return hits
        except Exception as e:
            logging.error(f"Search error: {str(e)}")
            raise