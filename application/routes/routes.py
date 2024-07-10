from fastapi import APIRouter
from .login import login_router
from .signup import signup_router
from .dashboard import index_route
from .login_cli_verify import verify_route

router = APIRouter()
router.include_router(router=login_router, prefix="/login")
router.include_router(router=signup_router, prefix="/signup")
router.include_router(router=verify_route, prefix="/login-cli-verify")
router.include_router(router=index_route, prefix="")