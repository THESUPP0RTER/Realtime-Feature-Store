from typing import List
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_session_context
from src.models import FeatureDefinition
from src.redis_client import get_redis_client
from src.schemas import IngestRequest, OnlineFeatureRequest, OnlineFeatureResponse

router = APIRouter()


@router.post("/register")
def register_feature(
    feature: FeatureDefinition,
    session: Session = Depends(get_session_context)
):
    """Register a new feature in the feature store"""
    if session.query(FeatureDefinition).filter(FeatureDefinition.id == feature.id).first():
        raise HTTPException(status_code=400, detail="Feature already exists")

    session.add(feature)
    session.commit()
    return {"message": "Feature registered"}


@router.get("/features")
def get_features(
    session: Session = Depends(get_session_context),
):
    """Get all available features"""
    features = session.query(FeatureDefinition).all()
    return {"features": features}


@router.delete("/features/{feature_id}")
def delete_feature(
    feature_id: int,
    session: Session = Depends(get_session_context)
):
    """Delete a feature by ID"""
    feature = session.query(FeatureDefinition).filter(FeatureDefinition.id == feature_id).first()

    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    session.delete(feature)
    session.commit()
    return {"message": f"Feature '{feature.name}' deleted successfully"}


@router.post("/features/ingest")
def ingest_features(
    request: IngestRequest,
    session: Session = Depends(get_session_context)
):
    """Ingest feature values into Redis for online serving"""
    redis_client = get_redis_client()

    ingested_features = []

    for feature_value in request.features:
        # Look up feature definition to get TTL
        feature_def = session.query(FeatureDefinition).filter(
            FeatureDefinition.name == feature_value.feature_name
        ).first()

        if not feature_def:
            raise HTTPException(
                status_code=404,
                detail=f"Feature '{feature_value.feature_name}' not registered"
            )

        # Redis key format: entity_id:feature_name
        redis_key = f"{request.entity_id}:{feature_value.feature_name}"

        # Serialize value to JSON
        value_json = json.dumps(feature_value.value)

        # Set value in Redis with TTL if specified
        if feature_def.ttl_seconds:
            redis_client.setex(redis_key, feature_def.ttl_seconds, value_json)
        else:
            redis_client.set(redis_key, value_json)

        ingested_features.append(feature_value.feature_name)

    return {
        "message": "Features ingested successfully",
        "entity_id": request.entity_id,
        "features": ingested_features
    }


@router.post("/features/online", response_model=List[OnlineFeatureResponse])
def get_online_features(request: OnlineFeatureRequest):
    """Retrieve online features for multiple entities"""
    redis_client = get_redis_client()

    results = []

    for entity_id in request.entity_ids:
        features_dict = {}

        for feature_name in request.feature_names:
            redis_key = f"{entity_id}:{feature_name}"
            value = redis_client.get(redis_key)

            if value:
                # Deserialize from JSON
                features_dict[feature_name] = json.loads(value)
            else:
                features_dict[feature_name] = None

        results.append(OnlineFeatureResponse(
            entity_id=entity_id,
            features=features_dict
        ))

    return results


@router.get("/features/online/{entity_id}")
def get_entity_features(
    entity_id: str,
    feature_names: str = None  # Comma-separated feature names
):
    """Retrieve all or specific features for a single entity"""
    redis_client = get_redis_client()

    # If feature_names provided, parse them
    if feature_names:
        requested_features = [f.strip() for f in feature_names.split(",")]
    else:
        # Get all keys for this entity
        pattern = f"{entity_id}:*"
        keys = redis_client.keys(pattern)
        requested_features = [key.split(":", 1)[1] for key in keys]

    features_dict = {}
    for feature_name in requested_features:
        redis_key = f"{entity_id}:{feature_name}"
        value = redis_client.get(redis_key)

        if value:
            features_dict[feature_name] = json.loads(value)
        else:
            features_dict[feature_name] = None

    return {
        "entity_id": entity_id,
        "features": features_dict
    }

