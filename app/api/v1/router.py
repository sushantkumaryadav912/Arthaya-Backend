from fastapi import APIRouter
from app.api.v1.stocks import router as stocks_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.predictions import router as predictions_router
from app.api.v1.models import router as models_router
from app.api.v1.agents import router as agents_router
from app.api.v1.reports import router as reports_router
from app.api.v1.watchlist import router as watchlist_router
from app.api.v1.data_sources import router as data_sources_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(stocks_router)
api_v1_router.include_router(analysis_router)
api_v1_router.include_router(predictions_router)
api_v1_router.include_router(models_router)
api_v1_router.include_router(agents_router)
api_v1_router.include_router(reports_router)
api_v1_router.include_router(watchlist_router)
api_v1_router.include_router(data_sources_router)

