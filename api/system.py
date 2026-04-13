from fastapi import APIRouter, HTTPException
from api.dependencies import controller


router = APIRouter(
    prefix="/api/system",
    tags=["System"]
)


@router.post("/wipe")
async def wipe_db():
    success = controller.wipe_database()

    if not success:
        raise HTTPException(status_code=500, detail="Failed to wipe database")

    return {"status": "ok", "message": "Database wiped successfully"}
