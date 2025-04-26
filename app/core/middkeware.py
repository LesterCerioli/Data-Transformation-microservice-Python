from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import logger

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Pré-processamento (antes da requisição)
        logger.info(f"Incoming request: {request.method} {request.url}")
        
        try:
            response = await call_next(request)
            
            
            logger.info(f"Request completed: {response.status_code}")
            return response
            
        except HTTPException as http_exc:
            logger.error(f"HTTP error: {http_exc.detail}")
            raise
        except Exception as exc:
            logger.critical(f"Unexpected error: {str(exc)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")


async def db_transaction_middleware(request: Request, call_next):
    
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    request.state.db = db  
    
    try:
        response = await call_next(request)
        db.commit()
        return response
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()