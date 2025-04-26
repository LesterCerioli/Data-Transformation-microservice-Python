import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, BackgroundTasks, status, HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.schemas.imports import ImportRequest, ImportResponse, ImportStatus
from app.services.import_service import ImportService
from app.core.database import get_db
from app.core.security import verify_api_key
from app.core.logger import logger
from app.models.import_job import ImportJob
from app.workers.import_worker import process_import_job

router = APIRouter(prefix="/imports", tags=["Medical Records Import"])

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

@router.post(
    "/",
    response_model=ImportResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Import medical records",
    description="Initiate an import job for medical records"
)
async def import_records(
    
    request: ImportRequest,
    background_tasks: BackgroundTasks,
    
    # Then parameters with defaults
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
) -> ImportResponse:
    """
    Initiate medical records import from external healthcare organization
    """
    try:
        import_service = ImportService(db)
        if not import_service.verify_organization_access(
            api_key, 
            request.source_org_id,
            request.destination_org_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization not authorized"
            )

        job_id = uuid.uuid4()
        new_job = ImportJob(
            id=job_id,
            source_org_id=request.source_org_id,
            destination_org_id=request.destination_org_id,
            status=ImportStatus.PENDING,
            parameters=request.parameters,
            callback_url=request.callback_url,
            created_by=request.created_by,
            records_processed=0,
            message="Job queued"
        )
        
        db.add(new_job)
        db.commit()
        
        logger.info("Import job created", extra={"job_id": str(job_id)})

        background_tasks.add_task(
            process_import_job,
            job_id=job_id,
            db_url=str(db.bind.url)
        )

        return ImportResponse(
            job_id=job_id,
            status=ImportStatus.PENDING,
            status_url=f"/imports/status/{job_id}",
            records_processed=0,
            message="Import job queued"
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Import failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Import process failed"
        )

@router.get(
    "/status/{job_id}",
    response_model=ImportResponse,
    summary="Check import status",
    description="Get current status of an import job"
)
async def get_import_status(
    # Required parameter first
    job_id: uuid.UUID,
    
    # Then parameters with defaults
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
) -> ImportResponse:
    """
    Check status of an import job
    """
    job = db.query(ImportJob).filter(ImportJob.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import job not found"
        )
    
    return ImportResponse(
        job_id=job.id,
        status=job.status,
        status_url=f"/imports/status/{job_id}",
        records_processed=job.records_processed,
        message=job.message or "Job in progress"
    )