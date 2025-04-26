from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, validator
from uuid import UUID

class TransferStatus(str, Enum):
    """Status of a medical record transfer"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"  # For LGPD/GDPR compliance

class TransferDirection(str, Enum):
    """Direction of the transfer"""
    EXPORT = "export"
    IMPORT = "import"

class TransferBase(BaseModel):
    """Base schema for medical record transfers"""
    record_id: UUID = Field(..., description="ID of the medical record being transferred")
    source_org_id: UUID = Field(..., description="Source healthcare organization ID")
    destination_org_id: UUID = Field(..., description="Destination healthcare organization ID")
    direction: TransferDirection = Field(..., description="Transfer direction (export/import)")

class TransferCreate(TransferBase):
    """Schema for creating new transfers"""
    parameters: Dict = Field(default_factory=dict, description="Transfer configuration parameters")
    callback_url: Optional[str] = Field(None, description="Callback URL for notifications")
    initiated_by: UUID = Field(..., description="User/system initiating the transfer")

    @validator('parameters')
    def validate_parameters(cls, v):
        if not isinstance(v, dict):
            raise ValueError("Parameters must be a dictionary")
        return v

class TransferUpdate(BaseModel):
    """Schema for updating transfers"""
    status: Optional[TransferStatus] = Field(None, description="Updated transfer status")
    details: Optional[Dict] = Field(None, description="Additional transfer details")
    records_processed: Optional[int] = Field(None, ge=0, description="Number of records processed")

class TransferInDBBase(TransferBase):
    """Base database model for transfers"""
    id: UUID
    status: TransferStatus = Field(default=TransferStatus.PENDING, description="Current transfer status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    audit_log: Optional[List[Dict]] = Field(None, description="Audit trail for compliance")

    class Config:
        from_attributes = True

class Transfer(TransferInDBBase):
    """Complete transfer schema for API responses"""
    message: Optional[str] = Field(None, description="Human-readable status message")
    links: Optional[Dict[str, str]] = Field(None, description="Related resource links")

class TransferSummary(BaseModel):
    """Lightweight transfer summary"""
    id: UUID
    status: TransferStatus
    direction: TransferDirection
    created_at: datetime
    source_org: str = Field(..., description="Source organization name")
    destination_org: str = Field(..., description="Destination organization name")

class TransferBatchResponse(BaseModel):
    """Response for batch transfer operations"""
    batch_id: UUID
    total_transfers: int
    pending: int
    completed: int
    failed: int
    transfers: List[TransferSummary]