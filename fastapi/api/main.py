from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import search, admin, upload
from .database import engine, Base
from clients.elasticsearch_config import ESClient
from clients.google_drive_client import GoogleDriveClient
import os
import uvicorn

app = FastAPI()

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
    
    global google_drive_client
    global es_client
    google_drive_client = GoogleDriveClient()
    es_client = ESClient(os.getenv("ELASTICSEARCH_URL", "http://tutoref_elasticsearch:9200"))
    app.state.google_drive_client = google_drive_client
    app.state.es_client = es_client
    
    await es_client.init_index()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
