

from pydantic import BaseModel
from sqlalchemy import UUID


class MedicalRecordBase(BaseModel):
    id: UUID
    patient_id: UUID
    organization_id: UUID
    
class MedicalRecordCreate(MedicalRecordBase):
    id: UUID | None = None  # Opcional na criação