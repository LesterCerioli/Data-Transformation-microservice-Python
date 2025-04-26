import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.core.config import settings

class Logger:
    def __init__(self):
        self.logger = logging.getLogger("medical_record")
        self.logger.setLevel(logging.DEBUG)
        
        
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        
        file_handler = RotatingFileHandler(
            'logs/medical_records.log',
            maxBytes=1024*1024*5,  # 5MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        
        self.logger.addHandler(file_handler)
        
        
        if settings.environment == "development":
            self.logger.addHandler(console_handler)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def debug(self, message: str):
        self.logger.debug(message)


logger = Logger()