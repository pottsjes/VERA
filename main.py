from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.database import init_db
from api.routes_items import router as items_router
from api.routes_analyze import router as analyze_router
from api.routes_wardrobe import router as wardrobe_router
from api.routes_recommend import router as recommend_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="V.E.R.A.", lifespan=lifespan)

app.include_router(items_router)
app.include_router(analyze_router)
app.include_router(wardrobe_router)
app.include_router(recommend_router)


@app.get("/")
async def root():
    return {"name": "V.E.R.A.", "status": "online"}
