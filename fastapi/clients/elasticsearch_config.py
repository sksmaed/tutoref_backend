from elasticsearch import AsyncElasticsearch, exceptions
import logging
from typing import Dict, List, Optional
from api.utils.doc_preprocessor import TeachingPlanProcessor

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
                "team": {"type": "keyword"},
                "semester": {"type": "keyword"},
                "category": {"type": "keyword"},
                "grade": {"type": "keyword"},
                "duration": {"type": "keyword"},
                "writer_name": {"type": "keyword"},
            }
        }

        index_exists = await self.client.indices.exists(index=self.index_name)
        if not index_exists:
            try:
                await self.client.indices.create(
                    index=self.index_name,
                    settings=settings,
                    mappings=mappings,
                )
                logging.info(f"Created index {self.index_name}")
            except exceptions.BadRequestError as e:
                logging.error(f"Elasticsearch create index failed: {e}")
                raise

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
    
    async def exists(self, doc_id: str) -> bool:
        """檢查文件是否存在"""
        return await self.client.exists_source(index=self.index_name, id=doc_id)

    async def search(self, query: str, writer_name: Optional[str] = None, filters: Optional[Dict] = None, top_k: int = 500) -> List[Dict]:
        """
        搜尋教案
        :param query: 搜尋關鍵字
        :param filters: 過濾條件
        :param top_k: 返回的結果數量
        :return: 符合條件的文檔列表
        """
        
        must_clauses = []
        
        if query.strip():
            must_clauses.append({
                "bool": {
                    "should": [
                        {
                            "match": {
                                "objectives": {
                                    "query": query,
                                    "boost": 1.0 
                                }
                            }
                        },
                        {
                            "match": {
                                "outline": {
                                    "query": query,
                                    "boost": 1.0
                                }
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            })


        if writer_name and writer_name.strip():
            must_clauses.append({
                "wildcard": {
                    "writer_name.keyword": {
                        "value": f"*{writer_name}*",
                        "case_insensitive": True
                    }
                }
            })

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

        if filters:
            for field, value in filters.items():
                if value:
                    keyword_fields = {"team", "category", "grade", "semester", "writer_name"}
                    es_field = f"{field}.keyword" if field in keyword_fields else field

                    if isinstance(value, list):
                        search_body["query"]["bool"]["filter"].append(
                            {"terms": {es_field: value}}
                        )
                    else:
                        search_body["query"]["bool"]["filter"].append(
                            {"term": {es_field: value}}
                        )

        try:
            response = await self.client.search(
                index=self.index_name,
                body=search_body,
            )
            hits = response["hits"]
            return hits
        except Exception as e:
            logging.error(f"Search error: {str(e)}")
            raise
