from fastapi import FastAPI
from app.api.files import router as files_router

app = FastAPI(
    title="Geospatial File Measurement API",
    description="Upload KML or zipped Shapefile data and calculate feature measurements.",
    version="1.0.0",
)

app.include_router(files_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Geospatial File Measurement API", "docs": "/docs"}
