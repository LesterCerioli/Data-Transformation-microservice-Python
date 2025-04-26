from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, JSON, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
from app.schemas.imports import ImportStatus
import uuid  # Adicione esta importação

class ImportJob(Base):
    __tablename__ = "import_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, 
               default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    source_org_id = Column(UUID(as_uuid=True), nullable=False)
    destination_org_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(Enum(ImportStatus), nullable=False, default=ImportStatus.PENDING)
    parameters = Column(JSON, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    callback_url = Column(String)
    records_processed = Column(Integer, default=0)
    total_records = Column(Integer)
    message = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_audited = Column(Boolean, default=False)