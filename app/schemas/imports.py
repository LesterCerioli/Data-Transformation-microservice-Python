from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID

class ImportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ImportRequest(BaseModel):
    # Campos obrigatórios (sem default) primeiro
    source_org_id: UUID
    destination_org_id: UUID
    created_by: UUID
    parameters: Dict[str, Any]
    
    # Campos opcionais (com default) depois
    callback_url: Optional[str] = Field(default=None)

class ImportResponse(BaseModel):
    # Campos obrigatórios primeiro
    job_id: UUID
    status_url: str
    
    # Campos com default depois
    status: ImportStatus = Field(default=ImportStatus.PENDING)
    records_processed: int = Field(default=0)
    total_records: Optional[int] = Field(default=None)
    message: str = Field(default="")