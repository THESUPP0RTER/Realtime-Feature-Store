# Realtime Feature Store

A lightweight, high-performance real-time feature store designed for machine learning applications. Built with FastAPI, PostgreSQL, and Redis to provide sub-10ms feature serving latency for real-time ML inference.

## Overview

This feature store provides a complete solution for managing ML features with:
- **Feature Registry**: PostgreSQL-based metadata storage for feature definitions
- **Online Store**: Redis-based storage for real-time feature serving with sub-10ms latency
- **RESTful API**: FastAPI endpoints for feature registration, ingestion, and retrieval
- **Point-in-time Correctness**: Foundation for historical feature queries (future enhancement)

## Architecture

```
┌─────────────────┐
│   FastAPI App   │  (Feature Management & Serving)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼──────┐
│ Redis │ │PostgreSQL│
│(Online│ │(Registry)│
│ Store)│ │          │
└───────┘ └──────────┘
```

- **PostgreSQL**: Stores feature definitions, metadata, and statistics
- **Redis**: Stores feature values for real-time serving with TTL support
- **FastAPI**: Provides REST API for all operations

## Features

-  Sub-10ms P95 latency for single entity feature retrieval
-  Feature versioning and metadata management
-  TTL-based feature expiration
-  Batch feature retrieval support
-  JSON-based flexible metadata storage
-  Feature statistics tracking (min, max, mean, std deviation)
-  Docker-based deployment

## Performance Benchmarks

Performance results from 1000 test entities with 4 features each:

### Single Entity Retrieval (1000 requests)

| Metric | Latency (ms) |
|--------|--------------|
| Min | 1.72 |
| Mean | 2.22 |
| Median (P50) | 2.16 |
| P95 | 2.61 |
| P99 | 3.38 |
| Max | 5.88 |
| Std Dev | 0.30 |

**✓ P95 latency well under 10ms target**

### Batch Retrieval - 10 Entities (100 requests)

| Metric | Latency (ms) |
|--------|--------------|
| Min | 4.41 |
| Mean | 4.93 |
| Median (P50) | 4.88 |
| P95 | 5.49 |
| P99 | 5.85 |
| Max | 5.85 |

**✓ Batch retrieval maintains sub-10ms P95**

### Batch Retrieval - 50 Entities (100 requests)

| Metric | Latency (ms) |
|--------|--------------|
| Min | 14.46 |
| Mean | 16.42 |
| Median (P50) | 16.49 |
| P95 | 17.76 |
| P99 | 19.58 |
| Max | 19.58 |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.9+ (for running benchmarks locally)

### Running the Feature Store

1. **Clone the repository**
   ```bash
   git clone https://github.com/THESUPP0RTER/Realtime-Feature-Store.git
   cd Realtime-Feature-Store
   ```

2. **Start the services**
   ```bash
   docker-compose up -d
   ```

   This will start:
   - FastAPI application on `http://localhost:8000`
   - PostgreSQL on `localhost:5432`
   - Redis on `localhost:6379`

3. **Verify the API is running**
   ```bash
   curl http://localhost:8000/docs
   ```

   Or visit `http://localhost:8000/docs` in your browser for interactive API documentation.

### Running Benchmarks

```bash
# Install dependencies
pip install requests

# Run benchmark
python3 benchmark.py
```

## API Usage

### 1. Register a Feature

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "user_age",
    "description": "User age in years",
    "data_type": "int",
    "entity": "user",
    "feature_group": "demographics",
    "ttl_seconds": 3600
  }'
```

### 2. Ingest Feature Values

```bash
curl -X POST http://localhost:8000/features/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "user_123",
    "features": [
      {
        "feature_name": "user_age",
        "value": 25
      }
    ]
  }'
```

### 3. Retrieve Features for Serving

**Single entity:**
```bash
curl "http://localhost:8000/features/online/user_123?feature_names=user_age"
```

**Batch retrieval:**
```bash
curl -X POST http://localhost:8000/features/online \
  -H "Content-Type: application/json" \
  -d '{
    "entity_ids": ["user_123", "user_456"],
    "feature_names": ["user_age"]
  }'
```

### 4. List All Features

```bash
curl http://localhost:8000/features
```

### 5. Delete a Feature

```bash
curl -X DELETE http://localhost:8000/features/{feature_id}
```

## Project Structure

```
.
├── src/
│   ├── api/
│   │   └── router.py          # API endpoints
│   ├── database.py             # PostgreSQL connection
│   ├── redis_client.py         # Redis connection
│   ├── models.py               # SQLModel feature definitions
│   ├── schemas.py              # Pydantic request/response schemas
│   └── main.py                 # FastAPI application
├── docker-compose.yml          # Service orchestration
├── Dockerfile                  # API container build
├── requirements.txt            # Python dependencies
└── benchmark.py                # Performance benchmarking tool
```

## Future Enhancements

- [ ] Historical feature store for point-in-time correctness
- [ ] Feature computation engine (streaming/batch)
- [ ] Feature monitoring and drift detection
- [ ] Multi-entity feature retrieval optimization
- [ ] Feature lineage tracking
- [ ] Data quality validation

## License

MIT License
