from fastapi import FastAPI
from app.api.pdf_routes import router as pdf_router
from app.api.citation_routes import router as citation_router
from app.api.query_routes import router as query_router
from app.api.auth_routes import router as auth_router
from app.api.semantic_routes import router as semantic_router
from app.api.evaluation_routes import router as evaluation_router
app = FastAPI()
app.include_router(pdf_router)
app.include_router(citation_router)
app.include_router(query_router)
app.include_router(auth_router)
app.include_router(semantic_router)
app.include_router(evaluation_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Scholar Assistant API"}