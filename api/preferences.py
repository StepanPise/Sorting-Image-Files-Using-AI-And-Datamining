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
    try:
        prefs = controller.system_repo.get_all_preferences()
        return {"status": "ok", "data": prefs}
    except Exception as e:
        print("GET PREFS ERROR:", e)
        return {"status": "error", "message": str(e)}


@router.post("/{key}")
async def update_preference(key: str, pref: PreferenceUpdate):
    try:
        controller.system_repo.set_preference(key, pref.value)
        return {"status": "ok"}
    except Exception as e:
        print("SAVE PREFS ERROR:", e)
        return {"status": "error", "message": str(e)}
