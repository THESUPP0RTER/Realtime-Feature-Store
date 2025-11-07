from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class FeatureValue(BaseModel):
    """Schema for a single feature value"""
    feature_name: str
    value: Any


class IngestRequest(BaseModel):
    """Schema for ingesting features for an entity"""
    entity_id: str
    features: List[FeatureValue]


class OnlineFeatureRequest(BaseModel):
    """Schema for retrieving features"""
    entity_ids: List[str]
    feature_names: List[str]


class OnlineFeatureResponse(BaseModel):
    """Schema for online feature response"""
    entity_id: str
    features: Dict[str, Any]
