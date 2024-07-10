from fastapi import APIRouter
from .login import login_router

router = APIRouter()
router.include_router(router=login_router, prefix="/login")