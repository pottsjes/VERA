import os
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["wardrobe"])

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_WARDROBE_DIR = os.path.join(_PROJECT_ROOT, "wardrobe")


@router.get("/wardrobe/{filename}")
async def wardrobe_file(filename: str):
    path = os.path.join(_WARDROBE_DIR, filename)
    if not os.path.isfile(path):
        return {"error": "File not found"}, 404
    return FileResponse(path)
