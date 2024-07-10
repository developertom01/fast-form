from fastapi import APIRouter
from .login import login_router
from .signup import signup_router
from .dashboard import index_route

router = APIRouter()
router.include_router(router=login_router, prefix="/login")
router.include_router(router=signup_router, prefix="/signup")
router.include_router(router=index_route, prefix="")