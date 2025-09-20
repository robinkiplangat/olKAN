from fastapi import FastAPI, Body, Depends

from app.core.hybrid_storage import get_storage_backend
from app.models.schemas import Dataset
from app.core.database import get_db

app = FastAPI(title="olKAN")

storage = get_storage_backend()

@app.post("/datasets")
async def create_dataset(dataset: Dataset = Body(...)):
    return await storage.create_dataset(dataset)

@app.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str):
    dataset = await storage.get_dataset(dataset_id)
    if dataset:
        return dataset
    return {"error": "Dataset not found"}

@app.get("/")
def root():
    return {"message": "Welcome to olKAN v2.0"}
