from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.medical_record import MedicalRecord
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordUpdate
from app.core.logger import logger
from datetime import datetime

class MedicalRecordRepository:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, record_data: MedicalRecordCreate) -> Optional[MedicalRecord]:
        """Cria um novo prontuário médico"""
        try:
            db_record = MedicalRecord(
                **record_data.dict(exclude_unset=True),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(db_record)
            self.db.commit()
            self.db.refresh(db_record)
            return db_record
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating medical record: {e}")
            return None

    async def get_by_id(self, record_id: UUID) -> Optional[MedicalRecord]:
        """Obtém um prontuário pelo ID"""
        try:
            return self.db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching record {record_id}: {e}")
            return None

    async def get_by_patient(self, patient_id: UUID) -> List[MedicalRecord]:
        """Obtém todos os prontuários de um paciente"""
        try:
            return self.db.query(MedicalRecord)\
                .filter(MedicalRecord.patient_id == patient_id)\
                .order_by(MedicalRecord.created_at.desc())\
                .all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching records for patient {patient_id}: {e}")
            return []

    async def get_by_organization(self, org_id: UUID) -> List[MedicalRecord]:
        """Obtém todos os prontuários de uma organização"""
        try:
            return self.db.query(MedicalRecord)\
                .filter(MedicalRecord.organization_id == org_id)\
                .order_by(MedicalRecord.created_at.desc())\
                .all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching records for organization {org_id}: {e}")
            return []

    async def update(self, record_id: UUID, update_data: MedicalRecordUpdate) -> Optional[MedicalRecord]:
        """Atualiza um prontuário existente"""
        try:
            db_record = self.get_by_id(record_id)
            if not db_record:
                return None

            update_data = update_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_record, field, value)
            
            db_record.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_record)
            return db_record
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating record {record_id}: {e}")
            return None

    async def delete(self, record_id: UUID) -> bool:
        """Remove um prontuário (soft delete)"""
        try:
            db_record = self.get_by_id(record_id)
            if not db_record:
                return False

            db_record.is_active = False
            db_record.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting record {record_id}: {e}")
            return False

    async def search_records(
        self,
        patient_id: Optional[UUID] = None,
        organization_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        is_anonymous: Optional[bool] = None
    ) -> List[MedicalRecord]:
        """Busca avançada de prontuários com filtros"""
        try:
            query = self.db.query(MedicalRecord)
            
            if patient_id:
                query = query.filter(MedicalRecord.patient_id == patient_id)
            if organization_id:
                query = query.filter(MedicalRecord.organization_id == organization_id)
            if start_date:
                query = query.filter(MedicalRecord.created_at >= start_date)
            if end_date:
                query = query.filter(MedicalRecord.created_at <= end_date)
            if is_anonymous is not None:
                query = query.filter(MedicalRecord.is_anonymous == is_anonymous)
            
            return query.order_by(MedicalRecord.created_at.desc()).all()
        except SQLAlchemyError as e:
            logger.error(f"Error searching records: {e}")
            return []