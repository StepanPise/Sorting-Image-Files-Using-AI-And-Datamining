from fastapi import APIRouter
from pydantic import BaseModel
from api.dependencies import controller


router = APIRouter(
    prefix="/api/locations",
    tags=["Locations"]
)


@router.get("/")
def get_locations():
    tree = controller.load_location_tree()
    return {'status': 'ok', 'data': tree}
