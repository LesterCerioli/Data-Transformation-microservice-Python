from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    POOL_SIZE: int = 20          
    MAX_OVERFLOW: int = 30       
    PORT: int = 3035             
    
    class Config:
        env_file = ".env"
        extra = "allow"          

settings = Settings()