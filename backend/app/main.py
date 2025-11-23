from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from .api.v1.api import api_router
from .api.v1.api import api_router

app = FastAPI(
    title="DD Investment API",
    description="투자 정보 및 시장 데이터 API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 필요 시 특정 오리진으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 라우터 포함
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Hello DD-Investment 🚀"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
