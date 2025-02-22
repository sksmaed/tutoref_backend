from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import search, admin, upload
from .database import engine, Base
from .elasticsearch_config import ESClient
import os

app = FastAPI()

es_client = ESClient(os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200"))

app.add_middleware (
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(search.router)
app.include_router(admin.router)
app.include_router(upload.router)

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    await es_client.init_index()

app.state.es_client = es_client