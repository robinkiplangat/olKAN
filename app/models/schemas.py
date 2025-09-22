from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Dataset(BaseModel):
    id: str = Field(..., pattern=r'^[a-z0-9-_]+$')
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)
    owner_org: str
    license_id: str

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
