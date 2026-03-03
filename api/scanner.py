import tkinter as tk
from tkinter import filedialog
from fastapi import APIRouter
from pydantic import BaseModel
from api.dependencies import controller
import asyncio

router = APIRouter(
    prefix="/api/scanner",
    tags=["Scanner"]
)


class ScanOptions(BaseModel):
    detect_faces: bool


class ProgressState(BaseModel):
    is_scanning: bool = False
    progress: float = 0.0
    message: str = ""

    def clear(self):
        self.is_scanning = False
        self.progress = 0.0
        self.message = ""

    def update_progress(self, prog_val, msg):
        self.progress = prog_val
        self.message = f"Processing: {msg}"


class ToggleRequest(BaseModel):
    use_current_folder_only: bool


progress_data = ProgressState()


@router.get("/progress")
def get_progress():
    return progress_data


@router.post("/")
async def scan_folder(options: ScanOptions):
    # tkinter for folder selection

    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_path = filedialog.askdirectory(title="Choose photos folder")
    root.destroy()

    progress_data.clear()

    if not folder_path:
        return {"status": "cancelled", "message": f"No folder selected"}

    await asyncio.to_thread(
        controller.analyze_folder,
        folder_path=folder_path,
        detect_faces=options.detect_faces,
        callback=progress_data.update_progress
    )

    if controller.criteria.subset_ids is not None:
        controller.criteria.subset_ids = list(controller.current_batch_ids)

    return {"status": "ok", "message": f"Scanned: {folder_path}"}


@router.post("/toggle-current-folder")
def toggle_current_folder(request: ToggleRequest):
    if request.use_current_folder_only:
        controller.criteria.subset_ids = list(controller.current_batch_ids)
    else:
        controller.criteria.subset_ids = None

    return {"status": "ok"}
