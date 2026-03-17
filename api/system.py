from fastapi import APIRouter
from api.dependencies import controller


router = APIRouter(
    prefix="/api/system",
    tags=["System"]
)


@router.post("/wipe")
async def wipe_db():
    try:
        success = controller.wipe_database()
        if success:
            return {"status": "ok", "message": "Database wiped successfully."}
        else:
            return {"status": "error", "message": "Failed to wipe database."}
    except Exception as e:
        print("WIPE DB ERROR:", e)
        return {"status": "error", "message": str(e)}
