from fastapi import APIRouter
from app.api.endpoints import predict, train, auth

api_router = APIRouter()

# Register endpoint sub-routers under clean versioned namespaces
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(predict.router, prefix="/predict", tags=["Prediction"])
api_router.include_router(train.router, prefix="/train", tags=["Training"])
