from fastapi import FastAPI
from app.routers import proxy

app = FastAPI(
    title="MLOps LLM-Gateway & Multi-Provider Proxy",
    version="1.0.0"
)

app.include_router(proxy.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "llm-gateway"}