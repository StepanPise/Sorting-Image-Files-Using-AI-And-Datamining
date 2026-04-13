import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from api.people import router as people_router
from api.scanner import router as scanner_router
from api.photos import router as photos_router
from api.locations import router as locations_router
from api.time import router as time_router
from api.others import router as others_router
from api.preferences import router as pref_router
from api.system import router as system_router
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(title="AI Photo Manager API")
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


app.include_router(people_router)
app.include_router(scanner_router)
app.include_router(photos_router)
app.include_router(locations_router)
app.include_router(time_router)
app.include_router(others_router)
app.include_router(pref_router)
app.include_router(system_router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"CRITICAL ERROR: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error"
        }
    )


@app.get("/", response_class=FileResponse)
def home():
    return "frontend/index.html"


if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)

# start chrome --app="http://127.0.0.1:8000/"
