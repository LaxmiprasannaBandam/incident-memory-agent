import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from routers import health, incidents
from services.hindsight import HindsightService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup tasks before the app begins serving requests."""
    settings = get_settings()
    logger.info("Starting Incident Memory Agent backend")
    logger.info(
        "Hindsight URL: %s | Bank: %s",
        settings.hindsight_base_url,
        settings.hindsight_bank_id,
    )
    hindsight = HindsightService()
    await hindsight.ensure_bank_exists()
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Incident Memory Agent",
    description="AI-powered incident response agent with Hindsight persistent memory.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(incidents.router)


@app.get("/")
def root():
    return {"message": "Incident Memory Agent API", "docs": "/docs"}
