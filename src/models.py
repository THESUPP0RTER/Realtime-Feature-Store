from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class FeatureDefinition(SQLModel, table=True):
    __tablename__ = "features"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None
    data_type: str #"int", "float", "embedding", "boolean"
    entity: str = Field(index=True) #entity type
    feature_group: Optional[str] = Field(default=None, index=True) #Group related features

    #metadata
    is_nullable: bool = Field(default=True)
    source: Optional[str] = None #Data source or table name
    transformation: Optional[str] = None #Aggregation, encoding, etc

    #Purely for numerical features
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean_value: Optional[float] = None
    std_dev: Optional[float] = None

    # cache ttl for precomputed features
    ttl_seconds: Optional[int] = Field(default=None)

    tags: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None