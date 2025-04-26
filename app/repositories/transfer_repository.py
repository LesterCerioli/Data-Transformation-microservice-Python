from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.transfer import TransferLog
from app.schemas.transfer import TransferStatus

class TransferRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_transfer(self, transfer: TransferLog) -> TransferLog:
        """Register a new transfer"""
        self.db.add(transfer)
        self.db.commit()
        self.db.refresh(transfer)
        return transfer

    def get_transfer(self, transfer_id: UUID) -> Optional[TransferLog]:
        """Get a transfer by ID"""
        return self.db.query(TransferLog).filter(TransferLog.id == transfer_id).first()

    def update_transfer_status(
        self,
        transfer_id: UUID,
        status: TransferStatus,
        details: Optional[str] = None
    ) -> Optional[TransferLog]:
        """Update status from a transfer"""
        transfer = self.get_transfer(transfer_id)
        if transfer:
            transfer.status = status
            if details:
                transfer.details = details
            self.db.commit()
            self.db.refresh(transfer)
        return transfer

    def get_transfers_by_record(
        self,
        record_id: UUID,
        limit: int = 100
    ) -> List[TransferLog]:
        """List transfers for a medical record"""
        return (
            self.db.query(TransferLog)
            .filter(TransferLog.record_id == record_id)
            .order_by(TransferLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_organization_transfers(
        self,
        org_id: UUID,
        status: Optional[TransferStatus] = None,
        limit: int = 100
    ) -> List[TransferLog]:
        """List transfers from an Organization"""
        query = self.db.query(TransferLog).filter(
            (TransferLog.source_org_id == org_id) |
            (TransferLog.destination_org_id == org_id)
        )
        
        if status:
            query = query.filter(TransferLog.status == status)
            
        return (
            query.order_by(TransferLog.created_at.desc())
            .limit(limit)
            .all()
        )