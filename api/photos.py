import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Optional
from api.dependencies import controller
from structures import FilterCriteria

router = APIRouter(
    prefix="/api/photos",
    tags=["Photos"]
)


@router.get("/")
async def get_photos(people: Optional[str] = Query(None), country: List[str] = Query(default=[]),
                     city: List[str] = Query(default=[]), use_current_folder: bool = Query(False)):
    temp_criteria = FilterCriteria()

    if people:
        # example = http://127.0.0.1:8000/api/photos?people=1,4,5
        temp_criteria.person_ids = [int(x)
                                    for x in people.split(",") if x.isdigit()]

    temp_criteria.country = country
    temp_criteria.city = city

    if use_current_folder:
        temp_criteria.subset_ids = list(controller.current_batch_ids)

    photos = controller.get_photos_from_repo_for_gallery(temp_criteria)

    return {"status": "ok", "count": len(photos), "data": photos}


@router.get("/{photo_id}/file")
async def get_photo_file(photo_id: int):

    photo = controller.photo_repo.get_by_id(photo_id)

    if not photo or "path" not in photo:
        raise HTTPException(
            status_code=404, detail="Photo not found in database")

    file_path = photo["path"]

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404, detail=f"File missing: {file_path}")

    return FileResponse(file_path)
