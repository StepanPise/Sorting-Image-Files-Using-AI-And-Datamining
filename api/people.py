from fastapi import APIRouter
from api.dependencies import controller

router = APIRouter(
    prefix="/api/people",
    tags=["People"]
)


@router.get("/")
def get_people():
    people = controller.get_all_people()
    return {"status": "ok", "count": len(people), "data": people}
