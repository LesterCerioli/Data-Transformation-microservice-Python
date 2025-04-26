import uuid
from sqlalchemy import JSON, Column, DateTime, Enum, text  # Added text import
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
from app.schemas.transfer import TransferStatus

class Transfer(Base):
    __tablename__ = "transfer_logs"
    __table_args__ = {
        'comment': 'Audit log for medical record transfers between organizations'
    }
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),  # Changed to gen_random_uuid()
        index=True,
        comment="Unique identifier for the transfer"
    )
    record_id = Column(
        UUID(as_uuid=True),
        index=True,
        nullable=False,
        comment="ID of the medical record being transferred"
    )
    source_org_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        comment="Source healthcare organization ID"
    )
    destination_org_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        comment="Destination healthcare organization ID"
    )
    status = Column(
        Enum(TransferStatus),
        nullable=False,
        default=TransferStatus.PENDING,
        server_default=text(f"'{TransferStatus.PENDING.value}'"),  # Improved syntax
        comment="Current status of the transfer"
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when transfer was initiated"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when transfer was last updated"
    )
    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when transfer was completed"
    )
    parameters = Column(
        JSON,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),  # Explicit jsonb type
        comment="Configuration parameters for the transfer"
    )
    error_details = Column(
        JSON,
        nullable=True,
        comment="Error details if transfer failed"
    )
    audit_log = Column(
        JSON,
        nullable=True,
        comment="Complete audit trail for compliance"
    )

    def __repr__(self):
        return f"<Transfer {self.id} [{self.status}]>"