import io
from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel
from typing import Optional
from api.dependencies import controller

router = APIRouter(
    prefix="/api/people",
    tags=["People"]
)


class PersonUpdate(BaseModel):
    name: Optional[str] = None


@router.get("/")
async def get_people():
    people = controller.get_all_people()
    return {"status": "ok", "count": len(people), "data": people}


@router.patch("/{person_id}")
async def update_person(person_id: int, request: PersonUpdate):
    if request.name is not None:
        controller.update_person_name(person_id, request.name)
        return {"status": "ok"}
    return {"status": "ignored"}


@router.get("/{person_id}/thumbnail")
async def get_thumbnail(person_id: int):
    pil_img = controller.get_person_thumbnail(person_id)
    if pil_img:
        pil_img = pil_img.convert("RGB")
        buf = io.BytesIO()
        pil_img.save(buf, format="JPEG")
        return Response(content=buf.getvalue(), media_type="image/jpeg")

    raise HTTPException(status_code=404, detail="Thumbnail not found")
