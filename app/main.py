from fastapi import FastAPI
from app.routers.herb_router import router as herb_router
from fastapi.responses import HTMLResponse 
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Herb RAG + LLM API")

app.include_router(herb_router, prefix="/herb", tags=["herb"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hoặc: ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h2>Chào bạn! Đây là backend LLM API. Hãy truy cập <a href='/docs'>/docs</a> để thử API.</h2>"
