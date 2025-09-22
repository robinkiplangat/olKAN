from sqlalchemy import Column, String, Integer, DateTime, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class DatasetDB(Base):
    __tablename__ = 'datasets'

    id = Column(String, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(String, nullable=False)
    tags = Column(ARRAY(String))
    owner_org = Column(String, nullable=False)
    license_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
