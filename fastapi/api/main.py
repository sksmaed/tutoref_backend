from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import search, admin, upload
from .database import engine, Base
from .elasticsearch_config import ESClient
import os
import uvicorn

app = FastAPI()

es_client = ESClient(os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200"))

app.add_middleware (
    CORSMiddleware,
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

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
