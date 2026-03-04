from fastapi import APIRouter
from api.dependencies import controller

router = APIRouter(
    prefix="/api/others",
    tags=["Others"]
)
