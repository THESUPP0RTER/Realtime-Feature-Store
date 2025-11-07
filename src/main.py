from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.routing import APIRoute

from src.api.router import router
from src.database import init_db
from src.redis_client import get_redis_client, close_redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database and Redis
    init_db()
    get_redis_client()  # Initialize Redis connection
    yield
    # Shutdown: Cleanup
    close_redis_client()


app = FastAPI(
    title="Realtime Feature Store",
    openapi_url="/openapi.json",
    docs_url="/docs",
    lifespan=lifespan,
)

app.include_router(router)

