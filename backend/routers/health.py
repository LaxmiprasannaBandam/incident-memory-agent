from fastapi import APIRouter
from services.hindsight import HindsightService

router = APIRouter()


@router.get("/health")
def health_check():
    """Health check endpoint. Confirms backend is running and Hindsight is reachable."""
    hindsight = HindsightService()
    hindsight_ok = hindsight.health_check()
    return {
        "status": "ok",
        "hindsight": "connected" if hindsight_ok else "unreachable",
    }
