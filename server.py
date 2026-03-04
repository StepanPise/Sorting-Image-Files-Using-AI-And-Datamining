import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.people import router as people_router
from api.scanner import router as scanner_router
from api.photos import router as photos_router
from api.locations import router as locations_router
from api.time import router as time_router
from api.others import router as others_router

app = FastAPI(title="AI Photo Manager API")
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

app.include_router(people_router)
app.include_router(scanner_router)
app.include_router(photos_router)
app.include_router(locations_router)
app.include_router(time_router)
app.include_router(others_router)


@app.get("/", response_class=FileResponse)
def home():
    return "frontend/index.html"


if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
