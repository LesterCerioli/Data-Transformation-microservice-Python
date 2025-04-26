from sqlalchemy import Boolean, Column, DateTime, JSON, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base  # Certifique-se que esta é sua Base correta
import uuid

class MedicalRecord(Base):
    __tablename__ = "medical_records"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),  # Para PostgreSQL 13+
        index=True
    )
    patient_id = Column(
        UUID(as_uuid=True),
        index=True,
        nullable=False  # Adicionei nullable=False pois parece ser obrigatório
    )
    organization_id = Column(
        UUID(as_uuid=True),
        index=True,
        nullable=False  # Adicionei nullable=False pois parece ser obrigatório
    )
    record_data = Column(
        JSON,
        nullable=False  # Assumindo que é obrigatório
    )
    created_at = Column(
        DateTime(timezone=True),  # Adicionei timezone para melhor consistência
        server_default=func.now(),  # Valor padrão no banco de dados
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),  # Atualiza automaticamente quando o registro é modificado
        nullable=False
    )
    is_anonymous = Column(
        Boolean,
        default=False,  # Valor padrão no Python
        server_default=text('false'),  # Valor padrão no banco de dados
        nullable=False
    )