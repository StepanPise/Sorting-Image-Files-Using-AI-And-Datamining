from fastapi import APIRouter
from pydantic import BaseModel

from api.dependencies import controller


router = APIRouter(
    prefix="/api/preferences",
    tags=["Preferences"]
)


class PreferenceUpdate(BaseModel):
    value: str


@router.get("/")
async def get_preferences():
    prefs = controller.get_preferences()
    return {"status": "ok", "data": prefs}


@router.post("/{key}")
async def update_preference(key: str, pref: PreferenceUpdate):
    controller.update_preference(key, pref.value)
    return {"status": "ok"}
