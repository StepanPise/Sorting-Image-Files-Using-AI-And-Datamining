from fastapi import APIRouter, Query
from pydantic import BaseModel
from api.dependencies import controller


router = APIRouter(
    prefix="/api/locations",
    tags=["Locations"]
)


@router.get("/")
async def get_locations(use_current_folder: bool = Query(False)):
    subset_ids = list(
        controller.current_batch_ids) if use_current_folder else None

    tree = controller.load_location_tree(subset_ids=subset_ids)

    return {'status': 'ok', 'data': tree}
