from typing import Optional
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.import_job import ImportJob
from app.models.organization import Organization
from app.core.logger import logger
from app.core.security import verify_api_key

class ImportService:
    def __init__(self, db: Session):
        self.db = db

    def verify_organization_access(self, api_key: str, source_org_id: UUID, destination_org_id: UUID) -> bool:
        """
        Verify if the API key has access to both source and destination organizations
        
        Args:
            api_key: The API key provided in the request
            source_org_id: UUID of the source organization
            destination_org_id: UUID of the destination organization
            
        Returns:
            bool: True if access is granted, False otherwise
        """
        try:
            
            if not verify_api_key(api_key):
                return False

            # Check if source organization exists and is active
            source_org = self.db.query(Organization).filter(
                Organization.id == source_org_id,
                Organization.is_active == True
            ).first()

            
            dest_org = self.db.query(Organization).filter(
                Organization.id == destination_org_id,
                Organization.is_active == True
            ).first()

            if not source_org or not dest_org:
                logger.warning(
                    "Organization verification failed",
                    extra={
                        "source_org_exists": bool(source_org),
                        "destination_org_exists": bool(dest_org)
                    }
                )
                return False

            # Additional business logic checks can be added here
            # For example: check if organizations are allowed to exchange data
            
            return True

        except Exception as e:
            logger.error(
                "Error verifying organization access",
                exc_info=True,
                extra={
                    "error": str(e),
                    "source_org_id": str(source_org_id),
                    "destination_org_id": str(destination_org_id)
                }
            )
            return False

    def get_import_job(self, job_id: UUID) -> Optional[ImportJob]:
        """
        Retrieve an import job by ID
        
        Args:
            job_id: UUID of the import job
            
        Returns:
            Optional[ImportJob]: The import job if found, None otherwise
        """
        return self.db.query(ImportJob).filter(ImportJob.id == job_id).first()