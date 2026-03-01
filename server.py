import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse

from api.people import router as people_router

app = FastAPI(title="AI Photo Manager API")


app.include_router(people_router)


@app.get("/", response_class=FileResponse)
def home():
    return "frontend/index.html"


if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
