import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.middleware import CustomMiddleware, db_transaction_middleware
from app.routes import records, imports, exports, health
from app.core.security import verify_api_key  # Importe a função de autenticação


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    
    logger.info("Starting Medical Records Microservice")
    yield
    
    logger.info("Shutting down Medical Records Microservice")


app = FastAPI(
    title="Medical Records Microservice",
    description="Microservice for importing/exporting medical records from different healthcare organizations",
    version="1.0.0",
    lifespan=lifespan,
    dependencies=[Depends(verify_api_key)]  # Autenticação global
)


app.add_middleware(CustomMiddleware)
app.middleware("http")(db_transaction_middleware)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health.router, tags=["Health"])
app.include_router(records.router, prefix="/records", tags=["Records"])
app.include_router(imports.router, prefix="/import", tags=["Imports"])
app.include_router(exports.router, prefix="/export", tags=["Exports"])

# Documentação OpenAPI customizada
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Medical Records API",
        version="1.0.0",
        description="API for medical records management",
        routes=app.routes,
    )
        
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.PORT,  # Porta configurável via settings
        log_level="info",
        reload=settings.DEBUG  # Recarregamento automático em desenvolvimento
    )