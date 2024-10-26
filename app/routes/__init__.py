from fastapi import APIRouter
from .weather import router as weather_router
from .forecast import router as forecast_router

router = APIRouter()

# Include all route modules here
router.include_router(weather_router)
router.include_router(forecast_router)

__all__ = ['router']