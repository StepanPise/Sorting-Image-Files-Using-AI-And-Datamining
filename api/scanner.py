import tkinter as tk
from tkinter import filedialog
from fastapi import APIRouter
from pydantic import BaseModel
from api.dependencies import controller

router = APIRouter(
    prefix="/api/scanner",
    tags=["Scanner"]
)


class ScanOptions(BaseModel):
    detect_faces: bool


@router.post("/")
async def scan_folder(options: ScanOptions):
    # tkinter for folder selection
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_path = filedialog.askdirectory(title="Choose photos folder")
    root.destroy()

    if not folder_path:
        return {"status": "cancelled", "message": f"No folder selected"}

    controller.analyze_folder(folder_path=folder_path,
                              detect_faces=options.detect_faces,
                              )

    return {"status": "ok", "message": f"Scanned: {folder_path}"}
