from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.import_job import ImportJob
from app.schemas.imports import ImportStatus

class ImportJobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, import_job: ImportJob) -> ImportJob:
        """Create a new importing job"""
        self.db.add(import_job)
        self.db.commit()
        self.db.refresh(import_job)
        return import_job

    def get_by_id(self, job_id: UUID) -> Optional[ImportJob]:
        """Get a job by ID"""
        return self.db.query(ImportJob).filter(ImportJob.id == job_id).first()

    def update_status(
        self, 
        job_id: UUID, 
        status: ImportStatus,
        message: Optional[str] = None
    ) -> Optional[ImportJob]:
        """Update job status"""
        job = self.get_by_id(job_id)
        if job:
            job.status = status
            if message:
                job.message = message
            self.db.commit()
            self.db.refresh(job)
        return job

    def list_by_organization(
        self, 
        organization_id: UUID,
        limit: int = 100,
        offset: int = 0
    ) -> List[ImportJob]:
        """List job by Organization"""
        return (
            self.db.query(ImportJob)
            .filter(
                (ImportJob.source_org_id == organization_id) |
                (ImportJob.destination_org_id == organization_id)
            )
            .order_by(ImportJob.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_active_imports_count(self, organization_id: UUID) -> int:
        """Conts imports by Organization"""
        return (
            self.db.query(ImportJob)
            .filter(
                ((ImportJob.source_org_id == organization_id) |
                 (ImportJob.destination_org_id == organization_id)),
                ImportJob.status.in_([
                    ImportStatus.PENDING,
                    ImportStatus.PROCESSING
                ])
            )
            .count()
        )