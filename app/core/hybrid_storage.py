import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from app.core.config import settings
from app.models.schemas import Dataset
from sqlalchemy import select
from app.core.database import get_db
from app.models.database_models import DatasetDB

class StorageBackend:
    async def create_dataset(self, dataset: Dataset) -> Dataset:
        pass

    async def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        pass

    async def list_datasets(self, limit: int = 100) -> List[Dataset]:
        pass

class FlatFileStorage(StorageBackend):
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    async def create_dataset(self, dataset: Dataset) -> Dataset:
        dataset.created_at = datetime.utcnow()
        dataset.updated_at = dataset.created_at

        file_path = self.data_dir / f"{dataset.id}.json"

        with open(file_path, 'w') as f:
            json.dump(dataset.dict(), f, indent=2, default=str)

        return dataset

    async def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        file_path = self.data_dir / f"{dataset_id}.json"

        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return Dataset(**data)
        except Exception:
            return None

    async def list_datasets(self, limit: int = 100) -> List[Dataset]:
        datasets = []
        files = sorted(self.data_dir.glob("*.json"))

        for file_path in files[:limit]:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                datasets.append(Dataset(**data))
            except Exception:
                continue

        return datasets

class DatabaseStorage(StorageBackend):
    async def create_dataset(self, dataset: Dataset) -> Dataset:
        async with get_db() as db:
            db_dataset = DatasetDB(
                id=dataset.id,
                title=dataset.title,
                description=dataset.description,
                tags=dataset.tags,
                owner_org=dataset.owner_org,
                license_id=dataset.license_id
            )
            db.add(db_dataset)
            await db.commit()
            await db.refresh(db_dataset)
            dataset.created_at = db_dataset.created_at
            dataset.updated_at = db_dataset.updated_at
        return dataset

    async def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        async with get_db() as db:
            result = await db.execute(select(DatasetDB).where(DatasetDB.id == dataset_id))
            db_dataset = result.scalar_one_or_none()
            if db_dataset:
                return Dataset(
                    id=db_dataset.id,
                    title=db_dataset.title,
                    description=db_dataset.description,
                    tags=db_dataset.tags or [],
                    owner_org=db_dataset.owner_org,
                    license_id=db_dataset.license_id,
                    created_at=db_dataset.created_at,
                    updated_at=db_dataset.updated_at
                )
        return None

    async def list_datasets(self, limit: int = 100) -> List[Dataset]:
        async with get_db() as db:
            result = await db.execute(select(DatasetDB).limit(limit))
            db_datasets = result.scalars().all()
            return [Dataset(
                id=d.id,
                title=d.title,
                description=d.description,
                tags=d.tags or [],
                owner_org=d.owner_org,
                license_id=d.license_id,
                created_at=d.created_at,
                updated_at=d.updated_at
            ) for d in db_datasets]

class HybridStorage(StorageBackend):
    def __init__(self):
        self.flat_file = FlatFileStorage()
        self.database = DatabaseStorage()

    async def create_dataset(self, dataset: Dataset) -> Dataset:
        # For hybrid, use database as primary
        return await self.database.create_dataset(dataset)

    async def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        return await self.database.get_dataset(dataset_id)

    async def list_datasets(self, limit: int = 100) -> List[Dataset]:
        return await self.database.list_datasets(limit)

def get_storage_backend() -> StorageBackend:
    if settings.storage_backend == "hybrid":
        return HybridStorage()
    elif settings.storage_backend == "database":
        return DatabaseStorage()
    else:
        return FlatFileStorage()
