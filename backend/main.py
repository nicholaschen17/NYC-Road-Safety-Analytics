from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import crashes, export, hotspots, zones

app = FastAPI(title="NYC Road Safety API", version="1.0.0", docs_url="/api/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(hotspots.router, prefix="/api/v1", tags=["hotspots"])
app.include_router(crashes.router, prefix="/api/v1", tags=["crashes"])
app.include_router(zones.router, prefix="/api/v1", tags=["zones"])
app.include_router(export.router, prefix="/api/v1", tags=["export"])
