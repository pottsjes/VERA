import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.database import init_db
from api.routes_items import router as items_router
from api.routes_analyze import router as analyze_router
from api.routes_wardrobe import router as wardrobe_router
from api.routes_recommend import router as recommend_router

STATIC_DIR = os.path.join(os.path.dirname(__file__), "frontend", "dist")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="V.E.R.A.", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items_router)
app.include_router(analyze_router)
app.include_router(wardrobe_router)
app.include_router(recommend_router)

# Serve React frontend in production
if os.path.isdir(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="static")

    @app.get("/{path:path}")
    async def serve_spa(request: Request, path: str):
        # Serve index.html for all non-API routes (SPA client-side routing)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
