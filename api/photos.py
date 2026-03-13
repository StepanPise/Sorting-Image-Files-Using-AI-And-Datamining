from datetime import datetime
import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Optional
from api.dependencies import controller
from filter_criteria import FilterCriteria
import tkinter as tk
from tkinter import filedialog

router = APIRouter(
    prefix="/api/photos",
    tags=["Photos"]
)


@router.get("/")
async def get_photos(people: Optional[str] = Query(None), country: List[str] = Query(default=[]),
                     city: List[str] = Query(default=[]), use_current_folder: bool = Query(False), date_from: Optional[str] = Query(None),
                     date_to: Optional[str] = Query(None)):
    temp_criteria = FilterCriteria()

    if people:
        # example = http://127.0.0.1:8000/api/photos?people=1,4,5
        temp_criteria.person_ids = [int(x)
                                    for x in people.split(",") if x.isdigit()]

    temp_criteria.country = country
    temp_criteria.city = city

    if date_from:
        temp_criteria.date_from = f"{date_from} 00:00:00"

    if date_to:
        temp_criteria.date_to = f"{date_to} 23:59:59"

    if use_current_folder:
        temp_criteria.subset_ids = list(controller.current_batch_ids)

    photos = controller.get_photos_from_repo_for_gallery(temp_criteria)

    existing_photos = [
        p for p in photos if "path" in p and os.path.exists(p["path"])]

    return {"status": "ok", "count": len(existing_photos), "data": existing_photos}


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


@router.post("/export")
async def export_filtered_photos(

    # code duplication
    people: Optional[str] = Query(None),
    country: List[str] = Query(default=[]),
    city: List[str] = Query(default=[]),
    use_current_folder: bool = Query(False),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None)
):
    criteria = FilterCriteria()

    if people:
        criteria.person_ids = [int(x)
                               for x in people.split(",") if x.isdigit()]

    criteria.country = country if country else None
    criteria.city = city if city else None

    if date_from:
        criteria.date_from = f"{date_from} 00:00:00"
    if date_to:
        criteria.date_to = f"{date_to} 23:59:59"

    if use_current_folder:
        criteria.subset_ids = list(controller.current_batch_ids)
    else:
        criteria.subset_ids = None

    photos = controller.get_photos_from_repo_for_gallery(criteria)

    if not photos:
        return {"status": "error", "message": "No photos match the current filters."}

    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    target_dir = filedialog.askdirectory(title="Select Export Directory")
    root.destroy()

    if not target_dir:
        return {"status": "error", "message": "Export cancelled"}

    count, errors = controller.export_photos(photos, target_dir)

    # Open the target folder after export
    try:
        os.startfile(target_dir)
    except Exception:
        pass

    return {"status": "ok", "exported": count, "errors": errors}
