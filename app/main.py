from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers.herb_router import router as herb_router
from app.routers.feedback_router import router as feedback_router

app = FastAPI(title="Herb RAG + LLM API")

app.include_router(herb_router, prefix="/herb", tags=["herb"])
app.include_router(feedback_router, prefix="", tags=["feedback"])

app.mount("/herb/images", StaticFiles(directory="app/data/images"), name="images")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h2>Chào bạn! Đây là backend LLM API. Hãy truy cập <a href='/docs'>/docs</a> để thử API.</h2>"
